TRANSPORTATION_MODES = [
    "Riding bus",
    "Riding bike",
    "Walking",
    "Riding mobility-on-demand shuttle",
    "Riding taxi",
    "Riding car",
    "Driving car",
]

# Standardized CSV columns for the project
COL_AGE_GROUP = "Age_Group"
COL_SEX_EN = "Sex"
COL_HEALTH = "Usual state of health"
COL_SCENARIO = "Scenario"
COL_ACTIVITY = "Kind of activities"
COL_DAY_OF_WEEK_EN = "Day of the week"
COL_DAY_OF_WEEK_JP = "Day_of_week_JP"
COL_AREA_CLASSIFICATION_JP = "Area_classification_JP"
COL_AREA_CLASSIFICATION_EN = "Area_classification_EN"
COL_SEX_JP = "Sex_JP"
COL_VALIDATION_VALUE = "validation_value"
SURVEY_TITLE = "Survey on Time Use and Leisure Activities 2021"
COL_SIMULATION = "Simulation"
COL_SE_RATIO_PCT = "Standard_Error_Ratio_Pct"
COL_SE_RATIO_FRACTION = "SE_Ratio_Fraction"
COL_REGION_JP = "Region_JP"
COL_REGION_EN = "Region_EN"
COL_SAMPLE_EDS = "Sample_EDs"
COL_SAMPLE_HOUSEHOLDS = "Sample_Households"
COL_SAMPLE_PERSONS_LEISURE = "Sample_Persons_Leisure"
COL_SAMPLE_PERSONS_TIME_USE = "Sample_Persons_Time_Use"
COL_SAMPLE_PERSONS_AVERAGE_TIME = "Sample_Persons_Average_Time"
SURVEY_MIE_TOTAL_SAMPLE_SIZE = 3372
COL_METRIC = "Metric"
COL_COUNT = "Count"
COL_SIMULATION_UUID = "simulation_uuid"
COL_AGENT_UUID = "agent_uuid"
COL_STARTING_TIME = "starting_time"
COL_END_TIME = "end_time"
COL_DURATION = "duration"
COL_NORMALIZED_DURATION = "normalized_duration"
COL_SIM_ACTIVITY = "activity"
COL_LOCATION = "location"
COL_NEXT_LOC = "next_loc"
COL_DAYS_SIMULATED = "days_simulated"
COL_AGE_YEAR = "Age_Year"
COL_START_X = "start_x"
COL_START_Y = "start_y"
COL_DEST_X = "dest_x"
COL_DEST_Y = "dest_y"
COL_DIST = "dist"
COL_X = "x"
COL_Y = "y"
COL_ID = "ID"
COL_LOCATION_NAME = "Location Name"
COL_START_LOCATION = "start_location"
COL_DEST_LOCATION = "dest_location"
COL_SEGMENT_INDEX = "Segment Index"
COL_TIME = "Time"
COL_SCHEDULE_ACTIVITY = "Activity"

# Standardized JSON keys for the project
KEY_EXTRA_PARAMS = "extra_params"
PARAM_MOD_POLICY = "agent_params.mod_policy"
PARAM_AGE = "agent_params.age"
PARAM_GENDER = "agent_params.gender"
PARAM_HEALTH = "agent_params.health"

SIM_SCENARIO_TO_VAL_SCENARIO_MAP = {
    "Mobility-on-demand shuttle: not available": "Scenario 1",
    "Mobility-on-demand shuttle: is Free when traveling within Tamaki-town": "Scenario 2",
    "Mobility-on-demand shuttle: costs 400 yen fixed when traveling within Tamaki-town": "Scenario 3",
    "Mobility-on-demand shuttle: costs 800 yen fixed when traveling within Tamaki-town": "Scenario 4",
}

ACTIVITY_COLOR_MAP = {
    "Sleep": "#1e3a5f",
    "Personal care": "#5b9bd5",
    "Meals": "#e8a838",
    "Housework": "#8fbc8f",
    "Caring or nursing": "#c9707d",
    "Child care": "#f4a6b8",
    "Shopping": "#d4a03c",
    "Watching TV": "#7b68ee",
    "Listening to the radio": "#9b8fcc",
    "Reading newspapers or magazines": "#6a5acd",
    "Rest and relaxation": "#87ceeb",
    "Learning": "#3cb371",
    "Self-education": "#2e8b57",
    "Training": "#228b22",
    "Hobbies and amusements": "#dda0dd",
    "Sports": "#ff6347",
    "Volunteer and social activities": "#20b2aa",
    "Social life": "#ff69b4",
    "Medical examination or treatment": "#cd5c5c",
    "Other activities": "#a9a9a9",
    "Arriving": "#d3d3d3",
    "Riding bus": "#ff8c00",
    "Riding bike": "#32cd32",
    "Walking": "#ffd700",
    "Riding mobility-on-demand shuttle": "#00ced1",
    "Riding taxi": "#ff4500",
    "Riding car": "#b22222",
    "Driving car": "#8b0000",
    "Unknown": "#808080",
}

SIM_ACTIVITY_TO_VAL_ACTIVIY_MAP = {
    "Sleep": "Sleep",
    "Personal care": "Personal care",
    "Meals": "Meals",
    "Housework": "Housework",
    "Caring or nursing": "Caring or nursing",
    "Child care": "Child care",
    "Shopping": "Shopping",
    "Watching TV": "Watching TV, listening to the radio, reading newspapers or magazines",
    "Listening to the radio": "Watching TV, listening to the radio, reading newspapers or magazines",
    "Reading newspapers or magazines": "Watching TV, listening to the radio, reading newspapers or magazines",
    "Rest and relaxation": "Rest and relaxation",
    "Learning": "Learning, self-education, and training (excluding schoolwork)",
    "Self-education": "Learning, self-education, and training (excluding schoolwork)",
    "Training": "Learning, self-education, and training (excluding schoolwork)",
    "Hobbies and amusements": "Hobbies and amusements",
    "Sports": "Sports",
    "Volunteer and social activities": "Volunteer and social activities",
    "Social life": "Social life",
    "Medical examination or treatment": "Medical examination or treatment",
    "Other activities": "Other activities",
    "Arriving": None,
    "Riding bus": "Riding bus",
    "Riding bike": "Riding bike",
    "Walking": "Walking",
    "Riding mobility-on-demand shuttle": "Riding mobility-on-demand shuttle",
    "Riding taxi": "Riding taxi",
    "Riding car": "Riding car",
    "Driving car": "Driving car",
}

VALIDATION_ACTIVITIES = list(
    dict.fromkeys(
        act for act in SIM_ACTIVITY_TO_VAL_ACTIVIY_MAP.values() if act is not None
    )
)

HEALTH_MAP = {
    "0_Total": "Total",
    "1_Excellent": "Good",
    "2_Good": "Good",
    "3_Fair": "Normal",
    "4_Not good": "Poor",
    "5_Poor": "Poor",
}

VALIDATION_COL_MAP = {
    "Age": COL_AGE_GROUP,
    "value": COL_VALIDATION_VALUE,
}

DAY_OF_WEEK_MAP = {
    "0_Total": "Total",
    "1_Average of days": "Average of days",
    "1_Weekly average": "Weekly average",
    "2_Weekday": "Weekday",
    "3_Saturday": "Saturday",
    "4_Sunday": "Sunday",
    "5_Average of Saturday and Sunday": "Average of Saturday and Sunday",
    "6_Average of weekdays": "Average of weekdays",
}

SEX_MAP = {
    "0_Both sexes": "Both sexes",
    "1_Male": "Male",
    "2_Female": "Female",
}

AGE_MAP = {
    "0_Total": "Total",
    "1_15 to 19 years old": "15 to 19 years old",
    "2_20 to 24 years old": "20 to 24 years old",
    "3_25 to 34 years old": "25 to 34 years old",
    "4_35 to 44 years old": "35 to 44 years old",
    "5_45 to 54 years old": "45 to 54 years old",
    "6_55 to 64 years old": "55 to 64 years old",
    "7_65 to 74 years old": "65 to 74 years old",
    "8_75 years old and over": "75 years old and over",
    "6_65 to 74 years old": "65 to 74 years old",
    "7_75 years old and over": "75 years old and over",
}

ACTIVITY_MAP = {
    "01_Sleep": "Sleep",
    "02_Personal care": "Personal care",
    "03_Meals": "Meals",
    "04_Commuting to and from school or work": "Commuting to and from school or work",
    "05_Work": "Work",
    "06_Schoolwork": "Schoolwork",
    "07_Housework": "Housework",
    "08_Caring or nursing": "Caring or nursing",
    "09_Child care": "Child care",
    "10_Shopping": "Shopping",
    "11_Moving (excluding commuting)": "Moving (excluding commuting)",
    "12_Watching TV, listening to the radio, reading newspapers or magazines": "Watching TV, listening to the radio, reading newspapers or magazines",
    "13_Rest and relaxation": "Rest and relaxation",
    "14_Learning, self-education, and training (excluding schoolwork)": "Learning, self-education, and training (excluding schoolwork)",
    "15_Hobbies and amusements": "Hobbies and amusements",
    "16_Sports": "Sports",
    "17_Volunteer and social activities": "Volunteer and social activities",
    "18_Social life": "Social life",
    "19_Medical examination or treatment": "Medical examination or treatment",
    "20_Other activities": "Other activities",
    "R1_Primary activities(Regrouped)": "Primary activities(Regrouped)",
    "R2_Secondary activities(Regrouped)": "Secondary activities(Regrouped)",
    "R3_Tertiary activities(Regrouped)": "Tertiary activities(Regrouped)",
}

QUESTIONNAIRE_A_COL_MAP = {
    "地域区分": COL_REGION_JP,
    "Regions": COL_REGION_EN,
    "Number of \nsample EDs": COL_SAMPLE_EDS,
    "Number of sample households": COL_SAMPLE_HOUSEHOLDS,
    "Leisure Activities": COL_SAMPLE_PERSONS_LEISURE,
    "Time Use\nActivities by Time of Day＊": COL_SAMPLE_PERSONS_TIME_USE,
    "Average Time of Main Activities": COL_SAMPLE_PERSONS_AVERAGE_TIME,
}


SE_RATIOS_COL_MAP = {
    "曜日": COL_DAY_OF_WEEK_JP,
    "地域区分": COL_AREA_CLASSIFICATION_JP,
    "男女": COL_SEX_JP,
    "Day of the week": COL_DAY_OF_WEEK_EN,
    "Area classification": COL_AREA_CLASSIFICATION_EN,
    "Sex": COL_SEX_EN,
}

ACTIVITIES = {
    "Sleep": {"duration": 60, "available_in": ["home", "lodging", "campground"]},
    "Personal care": {
        "duration": 20,
        "available_in": [
            "home",
            "lodging",
            "campground",
            "spa",
            "beauty_salon",
            "hair_care",
        ],
    },
    "Meals": {
        "duration": 20,
        "available_in": [
            "home",
            "establishment",
            "lodging",
            "campground",
            "bakery",
            "food",
            "restaurant",
            "convenience_store",
            "cafe",
            "meal_takeaway",
            "supermarket",
            "grocery_or_supermarket",
            "liquor_store",
        ],
    },
    "Housework": {
        "duration": 20,
        "available_in": ["home", "lodging", "campground", "laundry"],
    },
    "Caring or nursing": {"duration": 20, "available_in": ["home", "hospital"]},
    "Child care": {"duration": 20, "available_in": ["home", "park"]},
    "Shopping": {
        "duration": 20,
        "available_in": [
            "store",
            "atm",
            "clothing_store",
            "hardware_store",
            "electronics_store",
            "furniture_store",
            "home_goods_store",
            "book_store",
            "bicycle_store",
            "pet_store",
            "jewelry_store",
            "florist",
            "car_dealer",
        ],
    },
    "Watching TV": {
        "duration": 20,
        "available_in": ["home", "lodging", "campground", "book_store", "library"],
    },
    "Listening to the radio": {
        "duration": 20,
        "available_in": ["home", "lodging", "campground", "book_store", "library"],
    },
    "Reading newspapers or magazines": {
        "duration": 20,
        "available_in": ["home", "lodging", "campground", "book_store", "library"],
    },
    "Rest and relaxation": {
        "duration": 20,
        "available_in": [
            "home",
            "lodging",
            "campground",
            "park",
            "spa",
            "transit_station",
            "train_station",
            "parking",
            "point_of_interest",
            "locality",
            "sublocality",
            "political",
            "art_gallery",
            "museum",
            "tourist_attraction",
        ],
    },
    "Learning": {"duration": 20, "available_in": ["home", "book_store", "library"]},
    "Self-education": {
        "duration": 20,
        "available_in": ["home", "book_store", "library"],
    },
    "Training": {"duration": 20, "available_in": ["home", "book_store", "library"]},
    "Hobbies and amusements": {
        "duration": 20,
        "available_in": ["home", "lodging", "campground"],
    },
    "Sports": {"duration": 20, "available_in": ["campground", "gym", "park"]},
    "Volunteer and social activities": {
        "duration": 20,
        "available_in": ["place_of_worship", "local_government_office", "city_hall"],
    },
    "Social life": {
        "duration": 20,
        "available_in": [
            "establishment",
            "lodging",
            "campground",
            "bakery",
            "food",
            "restaurant",
            "convenience_store",
            "cafe",
            "meal_takeaway",
            "supermarket",
            "grocery_or_supermarket",
            "liquor_store",
            "gym",
            "park",
            "store",
            "atm",
            "clothing_store",
            "hardware_store",
            "electronics_store",
            "furniture_store",
            "home_goods_store",
            "book_store",
            "bicycle_store",
            "pet_store",
            "jewelry_store",
            "florist",
            "car_dealer",
            "funeral_home",
            "spa",
            "beauty_salon",
            "city_hall",
            "art_gallery",
            "museum",
            "tourist_attraction",
        ],
    },
    "Medical examination or treatment": {
        "duration": 20,
        "available_in": [
            "hospital",
            "doctor",
            "dentist",
            "pharmacy",
            "drugstore",
            "health",
        ],
    },
    "Other activities": {
        "duration": 20,
        "available_in": [
            "place_of_worship",
            "cemetery",
            "local_government_office",
            "city_hall",
            "bank",
            "accounting",
            "lawyer",
            "post_office",
            "police",
            "laundry",
            "travel_agency",
            "real_estate_agency",
            "insurance_agency",
            "electrician",
            "painter",
            "locksmith",
            "car_repair",
            "moving_company",
            "general_contractor",
            "roofing_contractor",
        ],
    },
    "Arriving": {"duration": 5, "available_in": None},
    "Riding bus": {"duration": 5, "available_in": None},
    "Riding bike": {"duration": 5, "available_in": None},
    "Walking": {"duration": 5, "available_in": None},
    "Riding mobility-on-demand shuttle": {"duration": 5, "available_in": None},
    "Riding taxi": {"duration": 5, "available_in": None},
    "Riding car": {"duration": 5, "available_in": None},
    "Driving car": {"duration": 5, "available_in": None},
}

TRAVEL_MODES = {
    "Riding bus": {"speed": 45},
    "Riding bike": {"speed": 20},
    "Walking": {"speed": 10},
    "Riding mobility-on-demand shuttle": {"speed": 55},
    "Riding taxi": {"speed": 60},
    "Riding car": {"speed": 60},
    "Driving car": {"speed": 60},
}
