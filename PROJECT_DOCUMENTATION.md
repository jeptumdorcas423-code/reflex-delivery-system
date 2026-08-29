notepad PROJECT\_DOCUMENTATION.md

\# Reflex Delivery System



\## 1. Project Overview



Reflex Delivery System is a web-based delivery management system designed to simplify the process of creating, assigning, tracking, and confirming deliveries.



The system allows delivery requests to be created with customer and item information. Each delivery is assigned a unique order code that can be used to retrieve delivery information and generate a QR code.



Delivery statuses progress through the following workflow:



\*\*Open → Assigned → Picked Up → Delivered\*\*



The system uses a FastAPI backend, PostgreSQL database, and web-based frontend. The backend provides REST API endpoints for managing deliveries, rider assignment, status updates, order lookup, QR-code generation, and delivery confirmation.



\## 2. Project Objectives



The main objectives of the Reflex Delivery System are to:



1\. Allow customers or staff to create delivery requests.

2\. Generate a unique order code for every delivery.

3\. Store delivery information securely in a PostgreSQL database.

4\. Allow dispatchers to assign deliveries to riders.

5\. Track the progress of each delivery using defined status transitions.

6\. Allow users to search for a delivery using its order code.

7\. Generate a QR code for each order.

8\. Allow customers to confirm a delivery after the rider has picked it up.

9\. Provide a REST API for communication between the frontend and backend.

10\. Deploy the system online so that it can be accessed through a web browser.





\## 3. Technologies Used



| Technology | Purpose |

|---|---|

| Python | Main programming language |

| FastAPI | Backend web framework and REST API |

| PostgreSQL | Database for storing delivery information |

| psycopg2 | Connects the FastAPI application to PostgreSQL |

| Uvicorn | Runs the FastAPI application server |

| HTML | Frontend structure |

| JavaScript | Frontend interaction and API communication |

| QRCode | Generates delivery QR codes |

| Pillow | Supports QR-code image generation |

| python-dotenv | Loads environment variables securely |

| Git | Version control |

| GitHub | Source-code repository |

| Render | Cloud deployment platform |





\## 4. System Architecture



The Reflex Delivery System uses a three-part architecture:



\### 4.1 Frontend



The frontend provides the user interface through which users interact with the delivery system. It allows users to create deliveries, view delivery information, assign riders, update delivery status, look up orders, and access QR-code functionality.



\### 4.2 Backend



The backend is built using FastAPI and provides REST API endpoints. It receives requests from the frontend, validates the data, performs the required operations, and communicates with the PostgreSQL database.



\### 4.3 Database



PostgreSQL stores the delivery records. The current MVP uses a single `deliveries` table containing customer information, delivery details, status information, order codes, and rider identifiers.



\### 4.4 System Flow



The basic flow of the system is:



\*\*Frontend → FastAPI Backend → PostgreSQL Database\*\*



When a user performs an action, the frontend sends a request to the FastAPI backend. The backend processes the request and, when necessary, reads from or writes to the PostgreSQL database. The response is then returned to the frontend.









\## 5. Database Design



The Reflex Delivery System uses PostgreSQL as its relational database.



The current MVP contains one database table called `deliveries`.



\### 5.1 Deliveries Table



| Field | Data Type | Constraint | Description |

|---|---|---|---|

| `id` | UUID | Primary Key | Unique identifier for each delivery |

| `order\_code` | TEXT | Unique | Unique code used to identify and track an order |

| `customer\_name` | TEXT | NOT NULL | Name of the customer |

| `customer\_phone` | TEXT | NOT NULL | Customer's phone number |

| `customer\_address` | TEXT | NOT NULL | Delivery destination |

| `item\_description` | TEXT | NOT NULL | Description of the item being delivered |

| `status` | TEXT | NOT NULL | Current delivery status |

| `rider\_id` | TEXT | NULL | Identifier of the assigned rider |





\### 5.2 Delivery Status



The application controls the delivery status using the following sequence:



\*\*Open → Assigned → Picked Up → Delivered\*\*



A delivery starts with the status `Open`. When a rider is assigned, it changes to `Assigned`. After the rider picks up the item, it changes to `Picked Up`. Finally, the delivery becomes `Delivered`.



\### 5.3 Database Relationships



The current MVP contains only the `deliveries` table. Therefore, there are currently no foreign-key relationships between tables.



The `rider\_id` field is stored as a text identifier and is not currently a foreign key. A future version could introduce a separate `riders` table and establish a foreign-key relationship.





\## 6. API Endpoints



The FastAPI backend provides the following REST API endpoints.



| Method | Endpoint | Purpose |

|---|---|---|

| GET | `/` | Checks whether the API is running |

| POST | `/deliveries` | Creates a new delivery |

| GET | `/deliveries` | Retrieves all deliveries |

| POST | `/deliveries/{delivery\_id}/assign` | Assigns a rider to a delivery |

| POST | `/deliveries/{delivery\_id}/status` | Updates the delivery status |

| GET | `/deliveries/order/{order\_code}` | Retrieves a delivery using its order code |

| GET | `/deliveries/order/{order\_code}/qr` | Generates a QR code for an order |

| POST | `/deliveries/order/{order\_code}/confirm` | Confirms a delivery |



\### 6.1 API Status Rules



The system prevents invalid delivery status changes.



The allowed sequence is:



\*\*Open → Assigned → Picked Up → Delivered\*\*



For example, a delivery cannot move directly from `Open` to `Delivered`. A rider must first be assigned and the item must be picked up before the delivery can be completed.



\### 6.2 Order Code and QR Code



Each delivery receives a unique order code in the format:



`ORD-XXXXXXXX`



The order code can be used to retrieve delivery information. The system can also generate a QR code containing the order code, allowing the order to be identified electronically.





\## 7. How the System Works



\### 7.1 Creating a Delivery



A delivery request is created by providing:



\- Customer name

\- Customer phone number

\- Customer address

\- Item description



The backend generates a unique UUID and order code. The delivery is saved in the PostgreSQL database with an initial status of `Open`.



\### 7.2 Assigning a Rider



A dispatcher can assign a rider to an available delivery.



The system first checks that the delivery exists and that its current status is `Open`. If valid, the rider identifier is stored in `rider\_id` and the delivery status changes to `Assigned`.



\### 7.3 Updating Delivery Status



The system uses controlled status transitions:



\*\*Open → Assigned → Picked Up → Delivered\*\*



This prevents invalid status changes and helps maintain a consistent delivery workflow.



\### 7.4 Tracking an Order



A user can search for a delivery using its unique `order\_code`.



The backend searches the PostgreSQL database and returns the delivery information and current status.



\### 7.5 QR Code Generation



The system generates a QR code containing the delivery's `order\_code`.



The QR code is returned as a PNG image and can be used to identify the order electronically.



\### 7.6 Delivery Confirmation



A delivery can be confirmed using its order code.



The system only allows confirmation when the delivery has reached the `Picked Up` status. Once confirmed, the status changes to `Delivered`.





\## 8. Deployment



The Reflex Delivery System is deployed using Render.



\### 8.1 Backend Deployment



The FastAPI backend is deployed as a Render Web Service.



\*\*Backend URL:\*\*

https://reflex-delivery-system-v9dp.onrender.com



The backend runs using Uvicorn with the following start command:



`uvicorn main:app --host 0.0.0.0 --port $PORT`



\### 8.2 Frontend Deployment



The frontend is deployed as a Render Static Site.



\*\*Frontend URL:\*\*

https://reflex-delivery-system-frontend.onrender.com



The frontend is served from the `frontend` directory.



\### 8.3 Database Deployment



The application uses a PostgreSQL database hosted on Render.



\*\*Database Service:\*\* `reflex-db`



The backend connects to the database through the `DATABASE\_URL` environment variable.



Database credentials are stored as environment variables and are not included in the source code.



\### 8.4 Source Code



The complete project source code is maintained on GitHub.



\*\*GitHub Repository:\*\*

https://github.com/jeptumdorcas423-code/reflex-delivery-system



\## 9. Testing



The Reflex Delivery System was tested to verify that the main delivery workflow operates correctly.



\### 9.1 API Availability Test



\*\*Test:\*\* Open the backend root endpoint.



\*\*Expected Result:\*\* The API returns:



`Reflex API is running`



\*\*Result:\*\* Passed.



\### 9.2 Create Delivery Test



\*\*Test:\*\* Submit a delivery containing customer details and item information.



\*\*Expected Result:\*\* A new delivery is created with a unique UUID, unique order code, and `Open` status.



\*\*Result:\*\* Passed.



\### 9.3 Retrieve Deliveries Test



\*\*Test:\*\* Request all deliveries.



\*\*Expected Result:\*\* The API returns the delivery records stored in PostgreSQL.



\*\*Result:\*\* Passed.



\### 9.4 Rider Assignment Test



\*\*Test:\*\* Assign a rider to a delivery with `Open` status.



\*\*Expected Result:\*\* The rider ID is stored and the status changes to `Assigned`.



\*\*Result:\*\* Passed.



\### 9.5 Status Transition Test



\*\*Test:\*\* Update the delivery through the required status sequence.



\*\*Expected Result:\*\*



`Assigned → Picked Up → Delivered`



Invalid status transitions should be rejected.



\*\*Result:\*\* Passed.



\### 9.6 Order Lookup Test



\*\*Test:\*\* Search for a delivery using its order code.



\*\*Expected Result:\*\* The corresponding delivery information is returned.



\*\*Result:\*\* Passed.



\### 9.7 QR Code Test



\*\*Test:\*\* Request a QR code using a valid order code.



\*\*Expected Result:\*\* The API returns a PNG QR-code image containing the order code.



\*\*Result:\*\* Passed.



\### 9.8 Delivery Confirmation Test



\*\*Test:\*\* Confirm a delivery after it reaches `Picked Up`.



\*\*Expected Result:\*\* The delivery status changes to `Delivered`.



\*\*Result:\*\* Passed.



\### 9.9 Deployment Test



\*\*Test:\*\* Access the deployed frontend and backend through their Render URLs.



\*\*Expected Result:\*\* The frontend loads successfully and the backend responds to API requests.



\*\*Result:\*\* Passed.



\## 10. Project Structure



The project is organized into separate frontend and backend components.



```text

reflex/

│

├── backend/

│   ├── main.py

│   ├── requirements.txt

│   └── venv/

│

├── frontend/

│   └── index.html

│

├── .gitignore

└── PROJECT\_DOCUMENTATION.md



\## 11. System Features



The Reflex Delivery System provides the following main features:



\### 11.1 Delivery Request Creation



Users can create delivery requests by entering the customer's name, phone number, address, and item description.



\### 11.2 Unique Order Identification



Every delivery is automatically assigned a unique order code in the format:



`ORD-XXXXXXXX`



This makes it easier to identify and retrieve individual deliveries.



\### 11.3 Rider Assignment



A dispatcher can assign a rider to an available delivery. The system records the rider identifier and changes the delivery status from `Open` to `Assigned`.



\### 11.4 Delivery Status Tracking



The system tracks delivery progress using controlled status transitions:



`Open → Assigned → Picked Up → Delivered`



This provides a clear view of the delivery lifecycle.



\### 11.5 Order Tracking



Users can retrieve delivery information by providing the unique order code.



\### 11.6 QR Code Generation



The system generates a QR code for each valid order code. The QR code can be used as an electronic identifier for the delivery.



\### 11.7 Delivery Confirmation



Customers can confirm an order after the rider has picked it up. Successful confirmation changes the delivery status to `Delivered`.



\### 11.8 Persistent Data Storage



Delivery records are stored in PostgreSQL, allowing information to remain available beyond individual application sessions.

\## 12. Security and Configuration



The system uses environment variables to protect configuration information and sensitive credentials.



\### 12.1 Environment Variables



The database connection is accessed through the `DATABASE\_URL` environment variable.



The database URL is not hard-coded into the application and is not stored directly in the public GitHub repository.



The `python-dotenv` package is used during local development to load environment variables from a `.env` file.



\### 12.2 CORS



The FastAPI backend uses Cross-Origin Resource Sharing (CORS) middleware to allow communication between the deployed frontend and backend.



\### 12.3 Sensitive Information



Database credentials and other sensitive configuration values should be stored as environment variables rather than committed to GitHub.



The `.gitignore` file is used to prevent files such as local environment configuration and Python virtual environments from being committed to the repository.



\## 13. Limitations and Future Improvements



Although the current Reflex Delivery System provides the core delivery workflow, the MVP has some limitations.



\### 13.1 Current Limitations



1\. The system currently uses a single `deliveries` database table.

2\. The `rider\_id` field is stored as text rather than being linked to a separate riders table.

3\. There is currently no user authentication or role-based access control.

4\. The current system does not include real-time GPS tracking.

5\. The application does not currently provide automated SMS or email notifications.

6\. The free Render instance may spin down after inactivity, which can cause slower initial requests.



\### 13.2 Future Improvements



Future versions could introduce:



1\. A separate `riders` table with a foreign-key relationship to deliveries.

2\. User authentication for customers, dispatchers, and riders.

3\. Role-based permissions.

4\. Real-time rider location tracking.

5\. SMS and email delivery notifications.

6\. A rider dashboard for viewing assigned deliveries.

7\. Customer accounts and delivery history.

8\. Delivery analytics and reporting.

9\. Improved QR-code scanning functionality.

10\. Automated deployment and testing pipelines.





\## 14. Conclusion



The Reflex Delivery System successfully provides a basic digital solution for managing delivery requests and tracking their progress.



The system combines a web-based frontend, FastAPI backend, and PostgreSQL database to support the complete delivery workflow from creation to confirmation. Unique order codes and QR codes provide convenient ways to identify deliveries, while controlled status transitions help maintain a consistent delivery process.



The project also demonstrates the use of REST APIs, relational database management, environment variables, Git version control, GitHub, and cloud deployment using Render.



The current system provides a foundation that can be expanded with authentication, rider management, real-time tracking, notifications, and analytics in future versions.











