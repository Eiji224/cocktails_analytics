from cocktails_analytics.services import get_db_engine
import pandas as pd

def get_most_viewed_cocktails():
    engine = get_db_engine()
    df = pd.read_sql(
        """
        SELECT
            c.id AS cocktail_id,
            c.name AS name,
            c.image_url AS image_url,
            COUNT(*) AS count
        FROM analytics_cocktailviews v
        JOIN cocktails_cocktail c ON c.id = v.cocktail_id
        GROUP BY c.id, c.name, c.image_url
        ORDER BY count DESC
        LIMIT 10
        """,
        engine,
    )

    return df.to_dict('records')