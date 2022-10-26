
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
#TODO: The cases, deaths etc are commulated, if we want separate days this is doable
def group_covid_by_date_cum(covid):
    last_seen_deaths = {}
    last_seen_cases = {}
    last_seen_tests = {}

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
            
            if (country_df.shape[0] != 0): #TODO: fix USA's holes in the data where its 0
                # total = country_df[["Deaths", "Cases", "Tests"]].sum()
                deaths = country_df["Deaths"].sum()
                cases = country_df["Cases"].sum()
                tests = country_df["Tests"].sum()

                last_seen_deaths = update_last_seen_dictionary(last_seen_deaths, code, deaths)
                last_seen_cases = update_last_seen_dictionary(last_seen_cases, code, cases)
                last_seen_tests = update_last_seen_dictionary(last_seen_tests, code, tests)

            covid_total = pd.concat([covid_total, pd.DataFrame({"Date": [date], 
                                            "Code": [code], 
                                            "Country": [country], 
                                            "Deaths": get_element_from_last_seen_dictionary(last_seen_deaths, code),
                                            "Cases": get_element_from_last_seen_dictionary(last_seen_cases, code),
                                            "Tests": get_element_from_last_seen_dictionary(last_seen_tests, code),
                                            "id": [id]
                                            })], ignore_index=True)
    covid_total.to_csv("covid_grouped.csv")

def update_last_seen_dictionary(dict, key, value):
    if(not math.isnan(value)):
        dict[key] = value
         
    return dict

def get_element_from_last_seen_dictionary(dict, key):
    if (not key in dict):
        #print(value)
        return 0
    else:
        return dict[key]
