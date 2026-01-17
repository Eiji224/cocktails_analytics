from cocktails_analytics.services import get_db_engine
import pandas as pd

def get_most_viewed_cocktails():
    engine = get_db_engine()
    df = pd.read_sql("SELECT id, viewed_at, cocktail_id, user_id FROM analytics_cocktailviews", engine)

    most_viewed = df.groupby('cocktail_id').size().reset_index(name='count')
    most_viewed = most_viewed.sort_values(by='count', ascending=False)

    return most_viewed.to_dict('records')