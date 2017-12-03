#!/usr/bin/env python3

import psycopg2

DBNAME = "news"

# What are the most popular three articles of all time?
most_popular_articles =  """select articles.title, count(*) as num
    from articles, log
    where log.status like '%200%'
    and log.path like concat('/article/', articles.slug)
    group by articles.title, log.path order by  num desc limit 3"""

# Who are the most popular article authors of all time?
most_popular_authors = """select authors.name, count(*) as num
    from articles, authors, log
    where log.status like '%200%'
    and log.path like concat('/article/', articles.slug)
    and articles.author = authors.id
    group by authors.name order by  num desc;"""

# When is the percentage of error is greater or equal to 1%?
percentage_of_errors = """
    select * from
      (select date, round(error_views * 100.0 / total_views, 1) as percent
      from
        (select t1.date, t1.total_views, t2.error_views
        from
            (select log.time::date as date, count(*) as total_views
                from log
                  group by log.time::date
                  order by log.time::date
            ) t1
        join
            (
            select log.time::date as date, count(*) as error_views
              from log
                where log.status != '200 OK'
                group by log.time::date
                order by log.time::date
            ) t2
        on
            t1.date = t2.date
        ) t3
      ) t4
    where percent>=1.0;
    """

# Are there any errors when the correct slug is requested?
errors_with_correct_slug = """
    select articles.slug, log.status
    from log, articles
    where log.path like concat('/article/', articles.slug)
    and log.status not like '%200%';
    """


queries = {
     'What are the most popular three articles of all time?'
        : most_popular_articles,
     'Who are the most popular article authors of all time?'
        : most_popular_authors,
     'Are there any errors when the correct slug is requested?'
        : errors_with_correct_slug
     }



def get_query_results(query):
    """Connects do Database, makes query and return results"""
    try:
        db = psycopg2.connect(database=DBNAME)
        c = db.cursor()
        c.execute(query)
        result = c.fetchall()
        db.close()
        return result
    except Exception as e:
        print(e)
        exit(1)


if __name__ == "__main__":
    for k, v in queries.items():
        print(k)
        res = get_query_results(v)
        if not res:
            print 'No results'
        else:
            for i, j in get_query_results(v):
                print(str(i) + ' - ' + str(j))
