# **Python Coding Patterns in Data Pipeline Design**

We will be working with the following code snippet

```python
# social_etl.py
# for complete code check out https://github.com/josephmachado/socialetl
import praw
import os
import sqlite3

REDDIT_CLIENT_ID='replace-with-your-reddit-client-id'
REDDIT_CLIENT_SECRET='replace-with-your-reddit-client-secret'
REDDIT_USER_AGENT='replace-with-your-Reddit-user-agent'

def extract():
    client = praw.Reddit(
        client_id=REDDIT_CLIENT_ID,
        client_secret=REDDIT_CLIENT_SECRET,
        user_agent=REDDIT_USER_AGENT,
    )
    subreddit = client.subreddit('dataengineering')
    top_subreddit = subreddit.hot(limit=100)
    data = []
    for submission in top_subreddit:
        data.append(
            {
                'title': submission.title,
                'score': submission.score,
                'id': submission.id,
                'url': submission.url,
                'comments': submission.num_comments,
                'created': submission.created,
                'text': submission.selftext,
            }
        )
    return data


def transform(data):
    """
    Function to only keep outliers.
    Outliers are based on num of comments > 2 standard deviations from mean
    """
    num_comments = [post.get('comments') for post in data]

    mean_num_comments = sum(num_comments) / len(num_comments)
    std_num_comments = (
        sum([(x - mean_num_comments) ** 2 for x in num_comments])
        / len(num_comments)
    ) ** 0.5
    return [
        post
        for post in data
        if post.get('comments') > mean_num_comments + 2 * std_num_comments
    ]


def load(data):
    # create a db connection
    conn = sqlite3.connect('./data/socialetl.db')
    cur = conn.cursor()
    try:
        # insert data into DB
        for post in data:
            cur.execute(
                """
                    INSERT INTO social_posts (
                        id, source, social_data
                    ) VALUES (
                        :id, :source, :social_data
                    )
                    """,
                {
                    'id': post.get('id'),
                    'score': post.get('score'),
                    'social_data': str(
                        {
                            'title': post.get('title'),
                            'url': post.get('url'),
                            'comments': post.get('num_comments'),
                            'created': post.get('created'),
                            'text': post.get('selftext'),
                        }
                    ),
                },
            )
    finally:
        conn.commit()
        conn.close()


def main():
    # pull data from Reddit
    data = extract()
    # transform reddit data
    transformed_data = transform(data)
    # load data into database
    load(transformed_data)
    
if __name__ == '__main__':
    main()
```


Functional Design
-  Predictable
- Atomicty - one function per task
- Idempotency - Running the same code with same input should provide the same output every time. UPSERT when loading data
- No Side Effects - Function should not modify anything outside it's scope, like closing database connection should be within the load function 

Factory Patterns
Creating objects in a sophisticated way
Creating right ETL objects

