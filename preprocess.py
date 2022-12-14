
import pandas as pd
import math
###  ---------- Data import and cleaning ----------  ###

codes = pd.read_json("country_codes.json")

#clean up the covid dataset
covid = pd.read_csv("covid2.csv")
covid = covid.merge(codes, left_on="Code", right_on="code")
covid.drop(["name", "code"], axis=1, inplace=True)


#Make dataframe for countries in the covid dataset
covid_countries = covid[["Country", "Code", "id"]].drop_duplicates()
#Date is date
covid["Date"] = pd.to_datetime(covid["Date"], dayfirst=True)

#Remove TOT from age for easier binning
covid = covid[covid["Age"] != "TOT"]

#Group by date for heatmap
def group_covid_by_date_cum(covid):
    last_seen_deaths = {}
    last_seen_cases = {}

    covid_total = pd.DataFrame()
    for date_df in covid.groupby("Date"):
        date = date_df[0] 
        print("Date: #" + str(date) + "#")
        #print(date)
        for index, row in covid_countries.iterrows():
            #if (pd.isna(code)):
            #    continue
            id = row["id"]
            country = row["Country"]
            code = row["Code"]
            country_df = date_df[1].loc[date_df[1]["Code"]==code]
            
            # if code == "US" and str(date) == "2020-05-19 00:00:00":
            #     print("Date: " + str(date) + "Shape[0]: " + str(country_df.shape[0]))

            if (country_df.shape[0] != 0): 
                # total = country_df[["Deaths", "Cases", "Tests"]].sum()
                deaths = country_df["Deaths"].sum()
                cases = country_df["Cases"].sum()

                # For bug finding
                # if code == "US" and str(date) == "2020-05-19 00:00:00":
                #     print("Date: " + str(date) + "Deaths: " + str(deaths))

                last_seen_deaths = update_last_seen_dictionary(last_seen_deaths, code, deaths, True)
                last_seen_cases = update_last_seen_dictionary(last_seen_cases, code, cases, True)

            covid_total = pd.concat([covid_total, pd.DataFrame({"Date": [date], 
                                            "Code": [code], 
                                            "Country": [country], 
                                            "Deaths": get_element_from_last_seen_dictionary(last_seen_deaths, code),
                                            "Cases": get_element_from_last_seen_dictionary(last_seen_cases, code),
                                            "id": [id]
                                            })], ignore_index=True)
    covid_total.to_csv("covid_grouped2.csv")

def locf(covid):
    last_seen_df = {country["Code"]: pd.DataFrame() for i, country in covid_countries.iterrows()}
    covid_imp = pd.DataFrame()
    # country_df = pd.DataFrame
    for index, row in covid_countries.iterrows():
        code = row["Code"]
        print(row["Country"])
        for date_df in covid.groupby("Date"):
            date = date_df[0]
            country_df = date_df[1].loc[date_df[1]["Code"]==code]
            if (country_df.shape[0] != 0): 
                last_seen_df[code] = country_df
            df = last_seen_df[code].copy()
            df["Date"] = date
            # country_df = pd.concat([country_df, df], ignore_index=True)
            covid_imp = pd.concat([covid_imp, df], ignore_index=True)
        # covid_imp = pd.concat([covid_imp, country_df], ignore_index=True)
        #break
    covid_imp.to_csv("covid_imputed.csv")




def update_last_seen_dictionary(dict, key, value, cumulative):
    if(not math.isnan(value)):
        val = value

        # Ensure that a smaller value isn't accidentally put in place of the actual value if cumulative
        # (e.g. for USA when the count was 0 because no entry was found but the value != NaN)
        if cumulative:
            prevVal = get_element_from_last_seen_dictionary(dict, key)
            val = val if (prevVal < val) else prevVal 

        dict[key] = val
         
    return dict

def get_element_from_last_seen_dictionary(dict, key):
    if (not key in dict):
        #print(value)
        return 0
    else:
        return dict[key]

def monthly_covid(covid_grouped):
    covid_grouped["Date"] = pd.to_datetime(covid_grouped["Date"], dayfirst=True)
    res  = covid_grouped.loc[covid_grouped["Date"].dt.is_month_end]
    res.to_csv("covid_monthly.csv")

 
# ----------- RUN PREPROCESSING ------------
# group_covid_by_date_cum(covid)
#covid_grouped = pd.read_csv("covid_grouped2.csv")
#monthly_covid(covid_grouped)
#locf(covid)