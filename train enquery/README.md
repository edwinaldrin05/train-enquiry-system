# 🚆 Train Enquiry System

<p align="center">
  <img src="overview_train.png" alt="Train Enquiry System Overview" width="100%">
</p>

<p align="center">
  <b>An interactive train search and enquiry application built with Python and Streamlit.</b>
</p>

<p align="center">
  <a href="https://train-enquiry-system-cmi9bwmbhz6zj7txr8ta7n.streamlit.app/">
    🌐 Live Demo
  </a>
</p>

---

## 📌 Project Overview

The **Train Enquiry System** is an interactive web application developed using **Python, Pandas, NumPy, Matplotlib, and Streamlit**.

The project covers the complete workflow from **data cleaning and exploratory data analysis (EDA)** to the development of an interactive train enquiry application.

Users can select a source station and destination station to search for direct trains and view important journey information such as departure time, arrival time, journey duration, distance, route type, and number of stops.

---

## 🌐 Live Application

### 🚆 Train Enquiry System

**Live Demo:**

https://train-enquiry-system-cmi9bwmbhz6zj7txr8ta7n.streamlit.app/

The application allows users to:

- Search direct trains between two stations
- Filter trains by route type
- Filter trains by maximum number of stops
- Sort search results
- View train journey details

---

## ✨ Features

- 🔎 Search direct trains between two stations
- 🚉 Source and destination station selection
- 🚆 Display available direct trains
- 🕐 Display departure and arrival times
- ⏱️ Calculate and display journey duration
- 📏 Display journey distance in kilometers
- 🛤️ Display route type
- 🛑 Display number of stops
- 🎯 Filter trains by route type
- 🎚️ Filter trains by maximum number of stops
- ↕️ Sort results by:
  - Departure Time
  - Journey Duration
  - Distance
- ⚠️ Handle cases where no direct trains are available
- 📊 Display total number of trains and stations

---

## 📊 Dataset

The Streamlit application uses the cleaned train dataset:

```text
data/train_cleaned.csv
