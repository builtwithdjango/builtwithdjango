import os
from collections import Counter
from datetime import datetime

import plotext as plt
import requests

# Get API key
api_key = os.getenv("BUTTONDOWN_API_TOKEN")
if not api_key:
    api_key = input("Please enter your Buttondown API token: ").strip()

# Set up API request
base_url = "https://api.buttondown.com/v1"
headers = {"Authorization": f"Token {api_key}", "Content-Type": "application/json"}

# Fetch all subscribers
all_subscribers = []
url = f"{base_url}/subscribers"

print("Fetching subscribers...")
while url:
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        data = response.json()
        subscribers = data.get("results", [])
        all_subscribers.extend(subscribers)

        print(f"Fetched {len(subscribers)} subscribers. Total so far: {len(all_subscribers)}")

        # Check for next page (adjust field name if needed)
        url = data.get("next")

    except requests.exceptions.RequestException as e:
        print(f"Error fetching subscribers: {e}")
        break

print(f"\nTotal subscribers fetched: {len(all_subscribers)}")

# Count risk scores
risk_score_counts = Counter()

for subscriber in all_subscribers:
    risk_score = subscriber.get("risk_score")
    risk_score_counts[risk_score] += 1

# Print risk score results table
print("\n" + "=" * 40)
print("RISK SCORE DISTRIBUTION")
print("=" * 40)
print(f"{'Risk Score':<15} {'Count':<10} {'Percentage':<10}")
print("-" * 40)

total_subscribers = len(all_subscribers)
for risk_score in sorted(risk_score_counts.keys(), key=lambda x: (x is None, x)):
    count = risk_score_counts[risk_score]
    percentage = (count / total_subscribers * 100) if total_subscribers > 0 else 0
    risk_score_display = "None" if risk_score is None else str(risk_score)
    print(f"{risk_score_display:<15} {count:<10} {percentage:>8.1f}%")

print("-" * 40)
print(f"{'TOTAL':<15} {total_subscribers:<10} {'100.0%':<10}")

# Count creation dates
creation_date_counts = Counter()
creation_year_counts = Counter()
creation_month_counts = Counter()

for subscriber in all_subscribers:
    creation_date = subscriber.get("creation_date")
    if creation_date:
        try:
            # Parse the date (format: "2020-09-29T00:00:00+00:00")
            dt = datetime.fromisoformat(creation_date.replace("Z", "+00:00"))

            # Count by full date
            date_str = dt.strftime("%Y-%m-%d")
            creation_date_counts[date_str] += 1

            # Count by year
            year_str = dt.strftime("%Y")
            creation_year_counts[year_str] += 1

            # Count by year-month
            month_str = dt.strftime("%Y-%m")
            creation_month_counts[month_str] += 1

        except ValueError:
            creation_date_counts["Invalid Date"] += 1
    else:
        creation_date_counts["None"] += 1

# Print creation date by year
print("\n" + "=" * 40)
print("CREATION DATE DISTRIBUTION BY YEAR")
print("=" * 40)
print(f"{'Year':<15} {'Count':<10} {'Percentage':<10}")
print("-" * 40)

for year in sorted(creation_year_counts.keys()):
    count = creation_year_counts[year]
    percentage = (count / total_subscribers * 100) if total_subscribers > 0 else 0
    print(f"{year:<15} {count:<10} {percentage:>8.1f}%")

print("-" * 40)
print(
    f"{'TOTAL':<15} {sum(creation_year_counts.values()):<10} {sum(creation_year_counts.values())/total_subscribers*100:>8.1f}%"
)

# Print creation date by month (last 12 months or top 20)
print("\n" + "=" * 40)
print("CREATION DATE DISTRIBUTION BY MONTH")
print("=" * 40)
print(f"{'Year-Month':<15} {'Count':<10} {'Percentage':<10}")
print("-" * 40)

# Show top 20 months or all if less than 20
sorted_months = sorted(creation_month_counts.items(), key=lambda x: x[0], reverse=True)
display_months = sorted_months[:20] if len(sorted_months) > 20 else sorted_months

for month, count in display_months:
    percentage = (count / total_subscribers * 100) if total_subscribers > 0 else 0
    print(f"{month:<15} {count:<10} {percentage:>8.1f}%")

if len(sorted_months) > 20:
    remaining_count = sum(count for _, count in sorted_months[20:])
    remaining_percentage = (remaining_count / total_subscribers * 100) if total_subscribers > 0 else 0
    print(f"{'... others':<15} {remaining_count:<10} {remaining_percentage:>8.1f}%")

print("-" * 40)
print(
    f"{'TOTAL':<15} {sum(creation_month_counts.values()):<10} {sum(creation_month_counts.values())/total_subscribers*100:>8.1f}%"
)

# Print top creation dates (if you want to see specific days)
print("\n" + "=" * 40)
print("TOP 10 CREATION DATES")
print("=" * 40)
print(f"{'Date':<15} {'Count':<10} {'Percentage':<10}")
print("-" * 40)

top_dates = creation_date_counts.most_common(10)
for date, count in top_dates:
    percentage = (count / total_subscribers * 100) if total_subscribers > 0 else 0
    print(f"{date:<15} {count:<10} {percentage:>8.1f}%")

# Create bar chart for creation dates by month
print("\n" + "=" * 60)
print("SUBSCRIBER CREATION CHART BY MONTH")
print("=" * 60)

# Prepare data for plotting - sort by date chronologically
sorted_months_chrono = sorted(creation_month_counts.items(), key=lambda x: x[0])

# Extract dates and counts
dates = [item[0] for item in sorted_months_chrono]
counts = [item[1] for item in sorted_months_chrono]

# Create the bar chart
plt.bar(dates, counts)
plt.title("Subscribers Created by Month")
plt.xlabel("Month")
plt.ylabel("Number of Subscribers")

# Rotate x-axis labels for better readability
plt.plotsize(120, 30)  # Make plot wider to accommodate date labels

plt.show()

# Also create a chart by year if there are multiple years
if len(creation_year_counts) > 1:
    print("\n" + "=" * 60)
    print("SUBSCRIBER CREATION CHART BY YEAR")
    print("=" * 60)

    # Prepare data for yearly chart
    sorted_years = sorted(creation_year_counts.items(), key=lambda x: x[0])
    years = [item[0] for item in sorted_years]
    year_counts = [item[1] for item in sorted_years]

    plt.clear_figure()  # Clear previous plot
    plt.bar(years, year_counts)
    plt.title("Subscribers Created by Year")
    plt.xlabel("Year")
    plt.ylabel("Number of Subscribers")
    plt.plotsize(80, 25)

    plt.show()

# Create chart for top creation dates (daily)
print("\n" + "=" * 60)
print("TOP 20 DAILY SUBSCRIBER CREATION CHART")
print("=" * 60)

# Get top 20 dates by subscriber count
top_20_dates = creation_date_counts.most_common(20)
top_dates_list = [item[0] for item in top_20_dates if item[0] not in ["None", "Invalid Date"]]
top_counts_list = [item[1] for item in top_20_dates if item[0] not in ["None", "Invalid Date"]]

if top_dates_list:
    plt.clear_figure()  # Clear previous plot
    plt.bar(top_dates_list, top_counts_list)
    plt.title("Top 20 Days by Subscriber Creation")
    plt.xlabel("Date")
    plt.ylabel("Number of Subscribers")
    plt.plotsize(140, 30)  # Make plot wider for date labels

    plt.show()
