TRANSPORTATION_MODES = [
    "Riding bus",
    "Riding bike",
    "Walking",
    "Riding mobility-on-demand shuttle",
    "Riding taxi",
    "Riding car",
    "Driving car",
]

SCENARIO_MAPPING = {
    "Mobility-on-demand shuttle: not available": "Scenario 1",
    "Mobility-on-demand shuttle: is Free when traveling within Tamaki-town": "Scenario 2",
    "Mobility-on-demand shuttle: costs 400 yen fixed when traveling within Tamaki-town": "Scenario 3",
    "Mobility-on-demand shuttle: costs 800 yen fixed when traveling within Tamaki-town": "Scenario 4",
}

ACTIVITY_COLORS = {
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

SIM_TO_ACTIVITY_MAPPING = {
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
}

COL_AGE = "Age"
COL_SEX = "Sex"
COL_HEALTH = "Usual state of health"
COL_SCENARIO = "Scenario"
COL_ACTIVITY = "Kind of activities"
COL_DAY_OF_WEEK = "Day of the week"
COL_VALIDATION = "Survey on Time Use and Leisure Activities 2021"
COL_SIMULATION = "Simulation"

QUESTIONNAIRE_A_COLS = [
    "Region_JP",
    "Region_EN",
    "Sample_EDs",
    "Sample_Households",
    "Sample_Persons_Leisure",
    "Sample_Persons_Time_Use",
    "Sample_Persons_Average_Time",
]

QUESTIONNAIRE_A_NUMERIC_COLS = [
    "Sample_EDs",
    "Sample_Households",
    "Sample_Persons_Leisure",
    "Sample_Persons_Time_Use",
    "Sample_Persons_Average_Time",
]

SE_RATIOS_ID_COLS = [
    "Day_of_week_JP",
    "Area_classification_JP",
    "Sex_JP",
    "Day_of_week_EN",
    "Area_classification_EN",
    "Sex_EN",
]

SE_RATIOS_ACTIVITIES = [
    "01_Sleep",
    "02_Personal care",
    "03_Meals",
    "04_Commuting to and from school or work",
    "05_Work",
    "06_Schoolwork",
    "07_Housework",
    "08_Caring or nursing",
    "09_Child care",
    "10_Shopping",
    "11_Moving (excluding commuting)",
    "12_Watching TV, listening to the radio, reading newspapers or magazines",
    "13_Rest and relaxation",
    "14_Learning, self-education, and training (excluding schoolwork)",
    "15_Hobbies and amusements",
    "16_Sports",
    "17_Volunteer and social activities",
    "18_Social life",
    "19_Medical examination or treatment",
    "20_Other activities",
    "R1_Primary activities(Regrouped)",
    "R2_Secondary activities(Regrouped)",
    "R3_Tertiary activities(Regrouped)",
]

AGENT_TRIPS_EXPORT_COLS = [
    "unique_simulation_id",
    "starting_time",
    "location",
    "next_loc",
    "start_x",
    "start_y",
    "dest_x",
    "dest_y",
]
