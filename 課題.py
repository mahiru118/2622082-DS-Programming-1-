import requests
from bs4 import BeautifulSoup
import time
import sqlite3

conn = sqlite3.connect("github.db")
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS repositories(
    name TEXT,
    language TEXT,
    stars TEXT
)
""")
cur.execute("DELETE FROM repositories")

page = 1

while True:
    url = f"https://github.com/google?page={page}&tab=repositories"
    time.sleep(1)
    res = requests.get(url)
    soup = BeautifulSoup(res.text, "html.parser")
    repos = soup.select("li")
    if len(repos) == 0:
        print("終了")
        break
    try:
        for repo in repos:

            name_tag = repo.find("a")
            if not name_tag:
                continue

            name = name_tag.text.strip()
            if name in [
                "Overview",
                "Repositories",
                "Projects",
                "Packages",
                "People",
                "Terms",
                "Privacy",
                "Security",
                "Status",
                "Community",
                "Docs",
                "Contact"
            ]:
                continue

            lang_tag = repo.find(attrs={"itemprop": "programmingLanguage"})
            language = lang_tag.text.strip() if lang_tag else "なし"
 
            star_tag = repo.find("a", href=lambda x: x and "stargazers" in x)
            stars = star_tag.text.strip() if star_tag else "0"

            cur.execute(
                "INSERT INTO repositories VALUES (?, ?, ?)",
                (name, language, stars)
            )
    except Exception as e:
        print(e)

    page += 1


conn.commit()

cur.execute("SELECT * FROM repositories")
rows = cur.fetchall()

for row in rows:
    print(row)

print("保存件数:", len(rows))

conn.close()