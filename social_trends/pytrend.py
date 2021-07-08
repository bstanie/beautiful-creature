import time
from datetime import timedelta, datetime

import pandas as pd
from pytrends.request import TrendReq


class AdaptedTrendReq(TrendReq):

    def get_historical_interest(self, keywords, year_start=2018, month_start=1,
                                day_start=1, hour_start=0, year_end=2018,
                                month_end=2, day_end=1, hour_end=0, cat=0,
                                geo='', gprop='', sleep=0):
        """Gets historical hourly data for interest by chunking requests to 1 week at a time (which is what Google allows)"""

        # construct datetime obejcts - raises ValueError if invalid parameters
        initial_start_date = start_date = datetime(year_start, month_start,
                                                   day_start, hour_start)
        end_date = datetime(year_end, month_end, day_end, hour_end)

        # the timeframe has to be in 1 week intervals or Google will reject it
        delta = timedelta(days=7)

        df = pd.DataFrame()

        date_iterator = start_date
        date_iterator += delta

        while True:
            # format date to comply with API call

            start_date_str = start_date.strftime('%Y-%m-%dT%H')
            date_iterator_str = date_iterator.strftime('%Y-%m-%dT%H')

            tf = start_date_str + ' ' + date_iterator_str

            try:
                self.build_payload(keywords, cat, tf, geo, gprop)
                week_df = self.interest_over_time()
                if df.shape[0] > 0 and df.index[-1] == week_df.index[0]:
                    multiplier = week_df[keywords].iloc[0] / df[keywords].iloc[-1]
                    df[keywords] *= multiplier
                    df = df.append(week_df.iloc[1:])
                else:
                    df = df.append(week_df)
            except Exception as e:
                print(e)
                pass

            start_date += delta
            date_iterator += delta

            if (date_iterator > end_date):
                # Run for 7 more days to get remaining data that would have been truncated if we stopped now
                # This is needed because google requires 7 days yet we may end up with a week result less than a full week
                start_date_str = start_date.strftime('%Y-%m-%dT%H')
                date_iterator_str = date_iterator.strftime('%Y-%m-%dT%H')

                tf = start_date_str + ' ' + date_iterator_str

                try:
                    self.build_payload(keywords, cat, tf, geo, gprop)
                    week_df = self.interest_over_time()
                    if df.shape[0] > 0 and df.index[-1] == week_df.index[0]:
                        multiplier = week_df[keywords].iloc[0] / df[keywords].iloc[-1]
                        df[keywords] *= multiplier
                        df = df.append(week_df.iloc[1:])
                    else:
                        df = df.append(week_df)
                except Exception as e:
                    print(e)
                    pass
                break

            # just in case you are rate-limited by Google. Recommended is 60 if you are.
            if sleep > 0:
                time.sleep(sleep)

        # Return the dataframe with results from our timeframe
        return df.loc[initial_start_date:end_date]
