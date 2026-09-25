# Green or Not? -- CO2 budget calculator (Week 1 big individual assignment)

# Reference values
FLIGHT_CO2_KG = 400          # kg CO2 per return short-haul flight
DRIVING_CO2_PER_KM = 0.23    # kg CO2 per km driven
MEAT_DIET_CO2_KG = 1400      # kg CO2 per year for a meat-heavy diet
SUSTAINABLE_BUDGET_KG = 2500 # kg CO2 sustainable annual budget

# Ask the user for their habits, converting each answer to the right type
flights = int(input("How many return flights do you take per year? "))
km_driven = float(input("How many kilometres do you drive per year? "))
eats_meat_daily = input("Do you eat meat daily? (yes/no) ").strip().lower() == "yes"

# Calculate total annual CO2
total_co2 = flights * FLIGHT_CO2_KG + km_driven * DRIVING_CO2_PER_KM
if eats_meat_daily:
    total_co2 += MEAT_DIET_CO2_KG

# Classify against the thresholds
if total_co2 < SUSTAINABLE_BUDGET_KG:
    classification = "under budget"
elif total_co2 <= 4000:
    classification = "slightly over budget"
else:
    classification = "far over budget"

# Print the type of one variable, as required
print(type(total_co2))

# Personalised summary
print(f"You emit {round(total_co2)} kg CO2 per year. That is {classification}.")
