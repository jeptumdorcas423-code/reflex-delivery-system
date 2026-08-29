from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from dotenv import load_dotenv
import psycopg2
import os
import uuid
import qrcode
from io import BytesIO

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_connection():
    return psycopg2.connect(os.getenv("DATABASE_URL"))


class Delivery(BaseModel):
    customer_name: str
    customer_phone: str
    customer_address: str
    item_description: str


@app.on_event("startup")
def create_table():

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS deliveries (
            id UUID PRIMARY KEY,
            order_code TEXT UNIQUE,
            customer_name TEXT NOT NULL,
            customer_phone TEXT NOT NULL,
            customer_address TEXT NOT NULL,
            item_description TEXT NOT NULL,
            status TEXT NOT NULL,
            rider_id TEXT
        )
    """)

    cursor.execute("""
        ALTER TABLE deliveries
        ADD COLUMN IF NOT EXISTS order_code TEXT
    """)

    cursor.execute("""
        UPDATE deliveries
        SET order_code = 'ORD-' || UPPER(SUBSTRING(id::text, 1, 8))
        WHERE order_code IS NULL
    """)

    cursor.execute("""
        CREATE UNIQUE INDEX IF NOT EXISTS deliveries_order_code_unique
        ON deliveries(order_code)
    """)

    connection.commit()

    cursor.close()
    connection.close()


@app.get("/")
def home():

    return {
        "message": "Reflex API is running"
    }


@app.post("/deliveries")
def create_delivery(delivery: Delivery):

    delivery_id = str(uuid.uuid4())

    order_code = (
        "ORD-" +
        str(uuid.uuid4())[:8].upper()
    )

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO deliveries
        (
            id,
            order_code,
            customer_name,
            customer_phone,
            customer_address,
            item_description,
            status,
            rider_id
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """, (
        delivery_id,
        order_code,
        delivery.customer_name,
        delivery.customer_phone,
        delivery.customer_address,
        delivery.item_description,
        "Open",
        None
    ))

    connection.commit()

    cursor.close()
    connection.close()

    return {
        "message": "Delivery request created",

        "delivery": {
            "id": delivery_id,
            "order_code": order_code,
            "customer_name": delivery.customer_name,
            "customer_phone": delivery.customer_phone,
            "customer_address": delivery.customer_address,
            "item_description": delivery.item_description,
            "status": "Open",
            "rider_id": None
        }
    }


@app.get("/deliveries")
def get_deliveries():

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            id,
            order_code,
            customer_name,
            customer_phone,
            customer_address,
            item_description,
            status,
            rider_id
        FROM deliveries
        ORDER BY id
    """)

    rows = cursor.fetchall()

    cursor.close()
    connection.close()

    deliveries = []

    for row in rows:

        deliveries.append({
            "id": str(row[0]),
            "order_code": row[1],
            "customer_name": row[2],
            "customer_phone": row[3],
            "customer_address": row[4],
            "item_description": row[5],
            "status": row[6],
            "rider_id": row[7]
        })

    return {
        "deliveries": deliveries
    }


@app.post("/deliveries/{delivery_id}/assign")
def assign_rider(
    delivery_id: str,
    rider_id: str
):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT status
        FROM deliveries
        WHERE id = %s
    """, (delivery_id,))

    row = cursor.fetchone()

    if not row:

        cursor.close()
        connection.close()

        return {
            "message": "Delivery not found"
        }

    current_status = row[0]

    if current_status != "Open":

        cursor.close()
        connection.close()

        return {
            "message": "Delivery is not available for assignment",
            "status": current_status
        }

    cursor.execute("""
        UPDATE deliveries
        SET
            rider_id = %s,
            status = 'Assigned'
        WHERE id = %s
    """, (
        rider_id,
        delivery_id
    ))

    connection.commit()

    cursor.close()
    connection.close()

    return {
        "message": "Rider assigned successfully",
        "delivery_id": delivery_id,
        "rider_id": rider_id,
        "status": "Assigned"
    }


@app.post("/deliveries/{delivery_id}/status")
def update_delivery_status(
    delivery_id: str,
    status: str
):

    allowed_transitions = {
        "Assigned": "Picked Up",
        "Picked Up": "Delivered"
    }

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT status
        FROM deliveries
        WHERE id = %s
    """, (delivery_id,))

    row = cursor.fetchone()

    if not row:

        cursor.close()
        connection.close()

        return {
            "message": "Delivery not found"
        }

    current_status = row[0]

    expected_status = allowed_transitions.get(
        current_status
    )

    if status != expected_status:

        cursor.close()
        connection.close()

        return {
            "message": "Invalid status transition",
            "current_status": current_status,
            "allowed_next_status": expected_status
        }

    cursor.execute("""
        UPDATE deliveries
        SET status = %s
        WHERE id = %s
    """, (
        status,
        delivery_id
    ))

    connection.commit()

    cursor.close()
    connection.close()

    return {
        "message": "Delivery status updated",
        "delivery_id": delivery_id,
        "status": status
    }


@app.get("/deliveries/order/{order_code}")
def get_delivery_by_order_code(
    order_code: str
):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            id,
            order_code,
            customer_name,
            customer_phone,
            customer_address,
            item_description,
            status,
            rider_id
        FROM deliveries
        WHERE order_code = %s
    """, (order_code,))

    row = cursor.fetchone()

    cursor.close()
    connection.close()

    if not row:

        return {
            "message": "Order not found"
        }

    return {
        "id": str(row[0]),
        "order_code": row[1],
        "customer_name": row[2],
        "customer_phone": row[3],
        "customer_address": row[4],
        "item_description": row[5],
        "status": row[6],
        "rider_id": row[7]
    }


@app.get("/deliveries/order/{order_code}/qr")
def generate_qr(order_code: str):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT id
        FROM deliveries
        WHERE order_code = %s
    """, (order_code,))

    row = cursor.fetchone()

    cursor.close()
    connection.close()

    if not row:

        return {
            "message": "Order not found"
        }

    qr = qrcode.QRCode(
        version=1,
        box_size=10,
        border=4
    )

    qr.add_data(order_code)
    qr.make(fit=True)

    image = qr.make_image(
        fill_color="black",
        back_color="white"
    )

    buffer = BytesIO()

    image.save(
        buffer,
        format="PNG"
    )

    buffer.seek(0)

    return StreamingResponse(
        buffer,
        media_type="image/png"
    )


@app.post("/deliveries/order/{order_code}/confirm")
def confirm_delivery(
    order_code: str
):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            id,
            status
        FROM deliveries
        WHERE order_code = %s
    """, (order_code,))

    row = cursor.fetchone()

    if not row:

        cursor.close()
        connection.close()

        return {
            "message": "Order not found"
        }

    delivery_id = row[0]
    current_status = row[1]

    # The customer can only confirm
    # an order after the rider has picked it up.

    if current_status != "Picked Up":

        cursor.close()
        connection.close()

        return {
            "message": "Order cannot be confirmed yet",
            "current_status": current_status,
            "required_status": "Picked Up"
        }

    cursor.execute("""
        UPDATE deliveries
        SET status = 'Delivered'
        WHERE id = %s
    """, (delivery_id,))

    connection.commit()

    cursor.close()
    connection.close()

    return {
        "message": "Order confirmed successfully",
        "order_code": order_code,
        "status": "Delivered"
    }