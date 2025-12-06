from flask import Flask
from minio import Minio
from minio.error import S3Error
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

    rows = ""
    try:
        for obj in client.list_objects(bucket_name, recursive=True):
            name = obj.object_name
            size = obj.size
            modified = obj.last_modified.isoformat() if obj.last_modified else ""
            rows += f"<tr><td>{name}</td><td>{modified}</td><td>{size}</td></tr>"
    except S3Error as e:
        rows = f"<tr><td colspan='3'>Error accessing MinIO bucket '{bucket_name}': {e.code} - {e.message}</td></tr>"

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
    <!DOCTYPE html>
    <html lang="en">
        <head>
            <meta charset="UTF-8" />
            <meta name="viewport" content="width=device-width, initial-scale=1.0" />
            <title>Jahn Consulting</title>
            <style>
                :root {{
                    --bg-badge: rgba(10, 15, 25, 0.9);
                    --text-primary: #f5f7fa;
                    --text-secondary: rgba(245, 247, 250, 0.7);
                    --link: rgba(245, 247, 250, 0.85);
                    --link-hover: #f5f7fa;
                    --shadow: 0 18px 45px rgba(0, 0, 0, 0.25);
                    --border-subtle: rgba(245, 247, 250, 0.08);
                    --accent-soft: rgba(245, 247, 250, 0.04);
                }}

                * {{
                    box-sizing: border-box;
                    margin: 0;
                    padding: 0;
                }}

                body {{
                    min-height: 100vh;
                    margin: 0;
                    font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
                    color: var(--text-primary);
                    background:
                        radial-gradient(circle at top left, rgba(88, 101, 242, 0.18), transparent 55%),
                        radial-gradient(circle at bottom right, rgba(0, 209, 255, 0.18), transparent 55%),
                        #050816;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    padding: 32px 16px;
                }}

                .shell {{
                    width: 100%;
                    max-width: 1120px;
                    background: rgba(10, 15, 25, 0.9);
                    border-radius: 24px;
                    box-shadow: var(--shadow);
                    border: 1px solid var(--border-subtle);
                    backdrop-filter: blur(18px);
                    padding: 28px 26px 26px;
                }}

                @media (min-width: 768px) {{
                    .shell {{
                        padding: 32px 32px 30px;
                    }}
                }}

                .shell-header {{
                    display: flex;
                    flex-wrap: wrap;
                    align-items: center;
                    justify-content: space-between;
                    gap: 12px 16px;
                    margin-bottom: 22px;
                }}

                .title-block h1 {{
                    font-size: 1.6rem;
                    letter-spacing: 0.02em;
                }}

                .title-block p {{
                    margin-top: 4px;
                    font-size: 0.9rem;
                    color: var(--text-secondary);
                }}

                .badge {{
                    display: inline-flex;
                    align-items: center;
                    gap: 8px;
                    padding: 6px 12px;
                    border-radius: 999px;
                    background: rgba(15, 23, 42, 0.85);
                    border: 1px solid var(--border-subtle);
                    color: var(--text-secondary);
                    font-size: 0.78rem;
                    letter-spacing: 0.08em;
                    text-transform: uppercase;
                }}

                .status-dot {{
                    width: 7px;
                    height: 7px;
                    border-radius: 50%;
                    background: #22c55e;
                    box-shadow: 0 0 0 4px rgba(34, 197, 94, 0.18);
                }}

                .layout {{
                    display: grid;
                    grid-template-columns: minmax(0, 1.1fr) minmax(0, 1fr);
                    gap: 18px;
                }}

                @media (max-width: 880px) {{
                    .layout {{
                        grid-template-columns: minmax(0, 1fr);
                    }}
                }}

                .panel {{
                    background: linear-gradient(145deg, rgba(15, 23, 42, 0.94), rgba(15, 23, 42, 0.86));
                    border-radius: 18px;
                    padding: 18px 18px 16px;
                    border: 1px solid var(--border-subtle);
                    box-shadow: 0 12px 30px rgba(0, 0, 0, 0.18);
                }}

                .panel-header {{
                    display: flex;
                    justify-content: space-between;
                    align-items: baseline;
                    gap: 10px;
                    margin-bottom: 10px;
                }}

                .panel-title {{
                    font-size: 1.02rem;
                    font-weight: 600;
                }}

                .panel-subtitle {{
                    font-size: 0.78rem;
                    color: var(--text-secondary);
                }}

                .bucket-pill {{
                    display: inline-flex;
                    align-items: center;
                    gap: 6px;
                    padding: 4px 10px;
                    border-radius: 999px;
                    background: var(--accent-soft);
                    border: 1px solid rgba(148, 163, 184, 0.22);
                    font-size: 0.75rem;
                    color: var(--text-secondary);
                }}

                .bucket-pill span {{
                    color: var(--text-primary);
                    font-weight: 500;
                }}

                .table-wrapper {{
                    margin-top: 8px;
                    border-radius: 14px;
                    overflow: hidden;
                    background: rgba(15, 23, 42, 0.9);
                    border: 1px solid rgba(15, 23, 42, 0.95);
                }}

                table {{
                    width: 100%;
                    border-collapse: collapse;
                    font-size: 0.86rem;
                }}

                thead {{
                    background: linear-gradient(90deg, rgba(15, 23, 42, 0.98), rgba(30, 64, 175, 0.7));
                }}

                th, td {{
                    padding: 10px 12px;
                    text-align: left;
                    white-space: nowrap;
                }}

                th {{
                    font-size: 0.78rem;
                    text-transform: uppercase;
                    letter-spacing: 0.08em;
                    color: var(--text-secondary);
                    border-bottom: 1px solid rgba(15, 23, 42, 0.9);
                }}

                tbody tr:nth-child(even) {{
                    background: rgba(15, 23, 42, 0.9);
                }}

                tbody tr:nth-child(odd) {{
                    background: rgba(15, 23, 42, 0.92);
                }}

                tbody tr:hover {{
                    background: rgba(37, 99, 235, 0.18);
                    transition: background 0.18s ease-out;
                }}

                td {{
                    border-bottom: 1px solid rgba(15, 23, 42, 0.95);
                    color: var(--text-primary);
                }}

                td:first-child, th:first-child {{
                    padding-left: 16px;
                }}

                td:last-child, th:last-child {{
                    padding-right: 16px;
                }}

                .fallback {{
                    text-align: center;
                    padding: 12px 16px 14px;
                    font-size: 0.86rem;
                    color: var(--text-secondary);
                }}

                a {{
                    color: var(--link);
                    text-decoration: none;
                }}

                a:hover {{
                    color: var(--link-hover);
                    text-decoration: underline;
                }}

                .footer {{
                    margin-top: 18px;
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    gap: 10px;
                    font-size: 0.78rem;
                    color: var(--text-secondary);
                }}

                .footer span {{
                    opacity: 0.8;
                }}
            </style>
        </head>
        <body>
            <main class="shell">
                <header class="shell-header">
                    <div class="title-block">
                        <h1>Storage & Customer Overview</h1>
                        <p>MinIO Objektspeicher und Postgres-Kundendaten in einer schlanken Admin-Ansicht.</p>
                    </div>
                    <div class="badge">
                        <span class="status-dot"></span>
                        <span>Docker Compose Demo UI</span>
                    </div>
                </header>

                <section class="layout">
                    <article class="panel">
                        <div class="panel-header">
                            <div>
                                <h2 class="panel-title">MinIO Files</h2>
                                <p class="panel-subtitle">Objekte im Bucket und ihre Metadaten.</p>
                            </div>
                            <div class="bucket-pill">
                                Bucket
                                <span>{bucket_name}</span>
                            </div>
                        </div>
                        <div class="table-wrapper">
                            <table>
                                <thead>
                                    <tr>
                                        <th>Filename</th>
                                        <th>Date</th>
                                        <th>Size (Bytes)</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {rows or "<tr><td colspan='3' class='fallback'>No objects found in this bucket.</td></tr>"}
                                </tbody>
                            </table>
                        </div>
                    </article>

                    <article class="panel">
                        <div class="panel-header">
                            <div>
                                <h2 class="panel-title">Customers</h2>
                                <p class="panel-subtitle">Daten aus der Postgres-Datenbank.</p>
                            </div>
                        </div>
                        <div class="table-wrapper">
                            <table>
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
                        </div>
                    </article>
                </section>

                <footer class="footer">
                    <span>Compose Demo UI · MinIO · Postgres</span>
                    <span><a href="https://www.jahnconsulting.io" target="_blank">Jahn Consulting</a></span>
                </footer>
            </main>
        </body>
    </html>
    """

    return html_content


@app.route('/api/data', methods=['GET'])
def get_data():
    """REST API endpoint that returns static HTML text"""

    html_content = """
    <!DOCTYPE html>
    <html lang="en">
        <head>
            <meta charset="UTF-8" />
            <meta name="viewport" content="width=device-width, initial-scale=1.0" />
            <title>Jahn Consulting</title>
            <style>
                :root {
                    --bg-badge: rgba(10, 15, 25, 0.9);
                    --text-primary: #f5f7fa;
                    --text-secondary: rgba(245, 247, 250, 0.7);
                    --link: rgba(245, 247, 250, 0.85);
                    --link-hover: #f5f7fa;
                    --shadow: 0 18px 45px rgba(0, 0, 0, 0.25);
                }

                body {
                    min-height: 100vh;
                    margin: 0;
                    font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
                    color: var(--text-primary);
                    background:
                        radial-gradient(circle at top left, rgba(88, 101, 242, 0.18), transparent 55%),
                        radial-gradient(circle at bottom right, rgba(0, 209, 255, 0.18), transparent 55%),
                        #050816;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    padding: 32px 16px;
                }

                .card {
                    max-width: 560px;
                    width: 100%;
                    background: rgba(10, 15, 25, 0.9);
                    border-radius: 20px;
                    padding: 24px 24px 22px;
                    box-shadow: var(--shadow);
                    border: 1px solid rgba(148, 163, 184, 0.2);
                    text-align: left;
                }

                h1 {
                    font-size: 1.4rem;
                    margin-bottom: 8px;
                }

                p {
                    margin: 4px 0;
                    font-size: 0.95rem;
                    color: var(--text-secondary);
                }
            </style>
        </head>
        <body>
            <div class="card">
                <h1>REST API Response</h1>
                <p>This is a static HTML text from the API.</p>
                <p>This is static HTML text from the API.</p>
            </div>
        </body>
    </html>
    """
    return html_content


if __name__ == '__main__':
    app.run()
