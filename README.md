# smart-telemedicine-triage-engine
AI-powered pre-consultation triage system using Machine Learning


## 📌 Problem

Telemedicine platforms allow patients to directly book consultations without prior screening.

This leads to:

* Delays in emergency care
* Doctors handling inappropriate cases
* Inefficient healthcare resource usage

---

## 💡 Solution

This project introduces an **AI-based triage system** that evaluates patients *before* consultation.

It calculates a **risk score (0–100)** based on:

* Symptoms
* Severity
* Age
* Medical history

### 🎯 Output:

* 🟢 Low Risk → Teleconsultation
* 🟡 Medium Risk → In-person visit
* 🔴 High Risk → Emergency care

---

## 🛠️ Tech Stack

* Python
* Streamlit
* Scikit-learn
* Pandas, NumPy

---

## ⚙️ Features

* 🔍 Intelligent symptom analysis
* 📊 Risk score with decision logic
* ⚡ Real-time recommendations
* 🖥️ Interactive UI

---

## 🧠 How It Works

1. User enters symptoms and details
2. System processes input using risk logic
3. Generates risk score
4. Suggests appropriate care level
5. takes bookings to hospitals
6. shows you your recent scores and appointments
7. contains your test reults and history
8. gives direct emergency numbers for ambulance 

---

## ▶️ Run Locally

```bash
streamlit run app.py
```

---

## 📂 Project Structure

```
app.py
requirements.txt
src/
   triage.py
   utils.py
   doctors.py
```

---

## 🚀 Future Improvements

* Integration with real hospital systems
* Multilingual support
* More advanced ML models

---

## 🏆 Hackathon

Built at **Healathon 2026** 

---



