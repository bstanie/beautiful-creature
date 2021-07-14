import datetime


def get_unix_timestamp(dt: datetime):
    unix_timestamp = (dt - datetime.datetime(1970, 1, 1)).total_seconds()
    return unix_timestamp


def get_datetime_from_unix(unix_timestamp):
    dt = datetime.datetime.fromtimestamp(unix_timestamp)
    return dt


def get_parent_post_ids(posts, keyword):
    ids = list(set([post["post_id"] for post in posts if post["num_comments"] > 0 and post["keyword"] == keyword]))
    return ids


def make_parent_post_filter_chunks(ids, chunk_size=20):
    chunks = [ids[l:l + chunk_size] for l in range(0, len(ids), chunk_size)]
    chunks = [",".join(chunk) for chunk in chunks]
    return chunks
