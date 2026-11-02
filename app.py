
from flask import Flask, render_template, abort

app = Flask(__name__)

POSTS = [
    {
        "slug": "understanding-cloud-security",
        "title": "Understanding Cloud Security",
        "summary": "An introduction to protecting cloud applications.",
        "body": "Cloud security combines identity, networking, encryption, monitoring, and secure configuration."
    },
    {
        "slug": "web-application-firewalls",
        "title": "Web Application Firewalls",
        "summary": "How WAF policies help protect web applications.",
        "body": "A WAF can inspect HTTP requests and apply rules to identify or block certain malicious traffic patterns."
    },
    {
        "slug": "identity-and-access-management",
        "title": "Identity and Access Management",
        "summary": "Why least privilege matters in cloud environments.",
        "body": "Least privilege limits identities to the permissions required for their tasks."
    }
]


@app.get("/")
def home():
    return render_template("index.html", posts=POSTS)


@app.get("/posts/<slug>")
def post_detail(slug):
    post = next((p for p in POSTS if p["slug"] == slug), None)

    if post is None:
        abort(404)

    return render_template("post.html", post=post)


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
