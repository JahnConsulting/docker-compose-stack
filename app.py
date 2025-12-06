from flask import Flask
from minio import Minio
import os
import psycopg2

app = Flask(__name__)




@app.route('/')
def hello_world():  # put application's code here

    endpoint = os.getenv("MINIO_ENDPOINT", f"{os.getenv('MINIO_API_HOST', 'minio-api.localhost')}")
    access_key = os.getenv("MINIO_ROOT_USER", os.getenv("MINIO_ACCESS_KEY", "minio"))
    secret_key = os.getenv("MINIO_ROOT_PASSWORD", os.getenv("MINIO_SECRET_KEY", "minio123"))
    bucket_name = os.getenv("MINIO_BUCKET", "uploads")

    client = Minio(
        endpoint,
        access_key=access_key,
        secret_key=secret_key,
        secure=False,
    )

    objects = client.list_objects(bucket_name, recursive=True)

    rows = ""
    for obj in objects:
        name = obj.object_name
        size = obj.size
        modified = obj.last_modified.isoformat() if obj.last_modified else ""
        rows += f"<tr><td>{name}</td><td>{modified}</td><td>{size}</td></tr>"

    db_host = os.getenv("POSTGRES_HOST")
    db_port = os.getenv("POSTGRES_INTERNAL_PORT") or os.getenv("POSTGRES_PORT")
    db_name = os.getenv("POSTGRES_DB")
    db_user = os.getenv("POSTGRES_USER")
    db_password = os.getenv("POSTGRES_PASSWORD")

    customer_rows = ""
    if not all([db_port, db_name, db_user, db_password]):
        missing = [name for name, value in [
            ("POSTGRES_INTERNAL_PORT/POSTGRES_PORT", db_port),
            ("POSTGRES_DB", db_name),
            ("POSTGRES_USER", db_user),
            ("POSTGRES_PASSWORD", db_password),
        ] if not value]
        customer_rows = f"<tr><td colspan='3'>Database configuration incomplete. Missing: {', '.join(missing)}</td></tr>"
    else:
        try:
            with psycopg2.connect(
                host=db_host,
                port=int(db_port),
                dbname=db_name,
                user=db_user,
                password=db_password,
            ) as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT id, firstname, lastname FROM customers ORDER BY id")
                    for cid, firstname, lastname in cur.fetchall():
                        customer_rows += f"<tr><td>{cid}</td><td>{firstname}</td><td>{lastname}</td></tr>"
        except Exception as e:
            customer_rows = f"<tr><td colspan='3'>Error loading customers: {e}</td></tr>"

    html_content = f"""
    <html>
        <head>
            <title>MinIO Files</title>
        </head>
        <body>
            <h1>Files in MinIO bucket '{bucket_name}'</h1>
            <table border=\"1\" cellpadding=\"4\" cellspacing=\"0\">
                <thead>
                    <tr>
                        <th>Filename</th>
                        <th>Date</th>
                        <th>Size (Bytes)</th>
                    </tr>
                </thead>
                <tbody>
                    {rows}
                </tbody>
            </table>

            <h2>Customers</h2>
            <table border=\"1\" cellpadding=\"4\" cellspacing=\"0\">
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>First Name</th>
                        <th>Last Name</th>
                    </tr>
                </thead>
                <tbody>
                    {customer_rows}
                </tbody>
            </table>
        </body>
    </html>
    """

    return html_content


@app.route('/api/data', methods=['GET'])
def get_data():
    """REST API endpoint that returns static HTML text"""

    html_content = """
    <html>
        <head>
            <title>API Response</title>
        </head>
        <body>
            <h1>REST API Response</h1>
            <p>This is a static HTML text from the API.</p>
            <p>This is static HTML text from the API.</p>
        </body>
    </html>
    """
    return html_content


if __name__ == '__main__':
    app.run()
