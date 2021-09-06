PLANS = {
    "Maintain current weight; 0 calories deficit": 0,
    "Lose .5lb per week; 250 calories deficit": -250,
    "Lose 1lb per week; 500 calories deficit": -500,
    "Lose 1.5lbs per week; 750 calories deficit": -750,
    "Gain .5lb per week; 250 calories surplus": 250,
    "Gain 1lb per week; 500 calories surplus": 500,
    "Gain 1.5lbs per week; 750 calories surplus": 750,
}
# https://www.healthline.com/health/fitness-exercise/how-many-calories-do-i-burn-a-day#calories-burned

ACTIVITY_LEVELS = {
    "Sedentary (little to no exercise)": 1.2,
    "Lightly active (light exercise 1–3 days per week)": 1.375,
    "Moderately active (moderate exercise 3–5 days per week)": 1.55,
    "Very active (hard exercise 6–7 days per week)": 1.725,
    "Extra active (very hard exercise, training, or a physical job)": 1.9,
}

BMI_LOW_NORMAL = 18.5

BMI_HIGH_NORMAL = 24.9

CATEGORIES = [
    (16, "Severe Thinness"),
    (17, "Moderate Thinness"),
    (18, "Mild Thinness"),
    (25, "Normal"),
    (30, "Overweight"),
    (35, "Obese Class I"),
    (40, "Obese Class II"),
    (100, "Obese Class III"),
]

BASE_API_URL = "https://api.spoonacular.com/"

BASE_INGREDIENTS_IMG_URL = "https://spoonacular.com/cdn/ingredients_100x100/"
