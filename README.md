# 🚦 AI City Brain

## 💡 Idea
AI City Brain is a multi-agent system that predicts, simulates, and optimizes city traffic based on real-world scenarios.

---

## 🧠 Features
- Scenario-based traffic simulation
- Traffic congestion prediction
- Traffic propagation modeling
- Smart routing & signal control
- Mobility recommendation (car, metro, bike)
- AI-generated explanations

---

## 🧩 System Pipeline

User Input  
↓  
Scenario Agent  
↓  
Traffic Prediction  
↓  
Congestion Detection  
↓  
Propagation  
↓  
Routing  
↓  
Mobility Recommendation  
↓  
Explanation Agent  
↓  
Final Output  

---

## 👥 Team Structure

| Branch | Responsibility |
|--------|--------------|
| person1-data | Traffic prediction + data |
| person2-scenario | Scenario parsing + propagation |
| person3-decision | Decision + routing + mobility |
| person4-integration | Orchestrator + explanation + UI |

---

## 📁 Project Structure
ai-city-brain/
│
├── backend/
│ ├── agents/
│ ├── utils/
│ └── orchestrator.py
│
├── frontend/
├── data/
│
├── main.py
├── requirements.txt
├── README.md
└── .gitignore



---

## ⚙️ Tech Stack
- Python
- Pandas
- Streamlit (optional UI)
- OpenAI API (optional)

---

## 🚀 How to Run

```bash
git clone https://github.com/DMANPRO/ai-city-brain.git
cd ai-city-brain
pip install -r requirements.txt
python main.py