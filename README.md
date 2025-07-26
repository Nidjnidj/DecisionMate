# 📈 DecisionMate

**DecisionMate** is a smart decision-making tool built with Streamlit that helps individuals and businesses evaluate and document decisions based on logic, emotion, and financial analysis.

---

## 🚀 Features

* ✅ **Personal Decision Support**
  Compare two life or career choices with:

  * SWOT Analysis
  * Priority Scoring
  * Radar Chart Visualization
  * Reflections & Emotions
  * Export to PDF and Excel

* 💼 **Business Decision Module**
  Evaluate CAPEX/OPEX-based decisions:

  * Input investment parameters
  * Calculate NPV & IRR
  * Tornado Sensitivity Chart
  * Downloadable CSV and PDF reports

* 🌐 **Multilingual Support**
  Switch between **English** and **Azerbaijani**

* 🔒 **Private Decision History**
  Each user has access to their own saved decisions

---

## 🖼️ Preview

---

## 🧰 Tech Stack

* [Streamlit](https://streamlit.io/) – App Framework
* [Plotly](https://plotly.com/) – Charts & Visualization
* [NumPy Financial](https://pypi.org/project/numpy-financial/) – IRR/NPV Calculation
* [FPDF](https://pyfpdf.github.io/fpdf2/) – PDF Generation
* [Pandas](https://pandas.pydata.org/) – Data Handling

---

## 🛠️ Run Locally

### Requirements

```bash
pip install -r requirements.txt
```

### Launch App

```bash
streamlit run app.py
```

---

## 📦 Folder Structure

```
DecisionMate/
|
├── app.py                  # Main Streamlit app
├── requirements.txt        # All Python dependencies
├── history.json            # Stores user decisions
├── nijat_logo.png          # Logo image
└── README.md               # This file
```

---

## 🤝 Contributing

Pull requests are welcome! For major changes, please open an issue first.

---

## 🧑‍💼 Author

**Nijat Isgandarov**
📧 [Contact](mailto:nijat.isgandarov89@gmail.com)

---

## 📃 License

[MIT](https://choosealicense.com/licenses/mit/)
