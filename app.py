import streamlit as st
import matplotlib.pyplot as plt


# ============================================================
# Page Configuration
# ============================================================

st.set_page_config(
    page_title="BMI Calculator",
    page_icon="⚖️",
    layout="centered"
)


# ============================================================
# BMI Calculation Function
# ============================================================

def calculate_bmi(weight, height):
    # Convert height from cm to meters
    height_m = height / 100

    # Calculate BMI
    bmi = weight / (height_m ** 2)

    # Calculate healthy weight range
    min_normal_weight = 18.5 * (height_m ** 2)
    max_normal_weight = 24.9 * (height_m ** 2)

    # Determine BMI category and advice
    if bmi < 18.5:
        category = "Underweight"

        weight_change = min_normal_weight - weight

        recommendation = (
            f"You could aim to gain approximately "
            f"{weight_change:.1f} kg to reach a BMI of 18.5."
        )

        advice = (
            "You are below the normal BMI range. "
            "Try eating nutritious, calorie-dense foods such as "
            "eggs, dairy products, nuts, rice, meat, and whole grains. "
            "Strength training may also help build healthy muscle."
        )

    elif bmi < 25:
        category = "Normal Weight"

        recommendation = (
            f"Your estimated healthy weight range is "
            f"{min_normal_weight:.1f}–{max_normal_weight:.1f} kg. "
            f"You are currently within this range."
        )

        advice = (
            "Your BMI is within the normal range. "
            "Keep maintaining a balanced diet, exercise regularly, "
            "stay hydrated, and get enough sleep."
        )

    elif bmi < 30:
        category = "Overweight"

        weight_change = weight - max_normal_weight

        recommendation = (
            f"You could aim to lose approximately "
            f"{weight_change:.1f} kg to reach a BMI of 24.9."
        )

        advice = (
            "Your BMI is above the normal range. "
            "Consider increasing physical activity and eating a "
            "balanced diet containing vegetables, fruits, whole grains, "
            "and lean proteins. Focus on gradual and sustainable changes."
        )

    else:
        category = "Obese"

        weight_change = weight - max_normal_weight

        recommendation = (
            f"You could aim to lose approximately "
            f"{weight_change:.1f} kg to reach a BMI of 24.9."
        )

        advice = (
            "Your BMI is in the obesity range. "
            "Consider gradually increasing physical activity and "
            "choosing nutrient-dense foods. A healthcare professional "
            "can help create a safe and personalized weight-management plan."
        )

    return (
        bmi,
        category,
        min_normal_weight,
        max_normal_weight,
        recommendation,
        advice
    )


# ============================================================
# BMI Graph
# ============================================================

def create_bmi_graph(bmi):

    fig, ax = plt.subplots(figsize=(10, 3))

    # Maximum BMI displayed on graph
    graph_max = 40

    # --------------------------------------------------------
    # Color-coded BMI sections
    # --------------------------------------------------------

    # Underweight: 0 - 18.5
    ax.barh(
        0,
        18.5,
        left=0,
        height=0.5,
        color="skyblue"
    )

    # Normal: 18.5 - 25
    ax.barh(
        0,
        6.5,
        left=18.5,
        height=0.5,
        color="green"
    )

    # Overweight: 25 - 30
    ax.barh(
        0,
        5,
        left=25,
        height=0.5,
        color="orange"
    )

    # Obese: 30 - 40
    ax.barh(
        0,
        10,
        left=30,
        height=0.5,
        color="red"
    )

    # --------------------------------------------------------
    # BMI Arrow
    # --------------------------------------------------------

    # Keep BMI marker inside graph
    marker_position = min(max(bmi, 0), graph_max)

    ax.annotate(
        f"BMI: {bmi:.1f}",
        xy=(marker_position, 0.25),
        xytext=(marker_position, 0.85),
        ha="center",
        va="bottom",
        fontsize=13,
        fontweight="bold",
        arrowprops=dict(
            arrowstyle="->",
            linewidth=3,
            color="black"
        )
    )

    # --------------------------------------------------------
    # Category Labels
    # --------------------------------------------------------

    ax.text(
        9.25,
        0,
        "Underweight",
        ha="center",
        va="center",
        fontsize=10,
        fontweight="bold"
    )

    ax.text(
        21.75,
        0,
        "Normal",
        ha="center",
        va="center",
        fontsize=10,
        fontweight="bold"
    )

    ax.text(
        27.5,
        0,
        "Overweight",
        ha="center",
        va="center",
        fontsize=10,
        fontweight="bold"
    )

    ax.text(
        35,
        0,
        "Obese",
        ha="center",
        va="center",
        fontsize=10,
        fontweight="bold"
    )

    # --------------------------------------------------------
    # Graph Formatting
    # --------------------------------------------------------

    ax.set_xlim(0, graph_max)
    ax.set_ylim(-0.6, 1.1)

    ax.set_xlabel("BMI", fontsize=11)

    ax.set_yticks([])

    ax.set_title(
        "BMI Classification",
        fontsize=14,
        fontweight="bold"
    )

    # Remove unnecessary borders
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_visible(False)

    plt.tight_layout()

    return fig


# ============================================================
# Streamlit Application
# ============================================================

st.title("⚖️ BMI Calculator")

st.write(
    "Adjust your weight and height using the sliders "
    "to calculate your BMI and see where you fall "
    "on the BMI classification scale."
)


# ============================================================
# Input Sliders
# ============================================================

weight = st.slider(
    "Weight (kg)",
    min_value=30.0,
    max_value=200.0,
    value=70.0,
    step=0.5
)

height = st.slider(
    "Height (cm)",
    min_value=100,
    max_value=220,
    value=170,
    step=1
)


# ============================================================
# Calculate Results
# ============================================================

(
    bmi,
    category,
    min_normal_weight,
    max_normal_weight,
    recommendation,
    advice
) = calculate_bmi(weight, height)


# ============================================================
# Results
# ============================================================

st.subheader("Your Results")

col1, col2 = st.columns(2)

with col1:
    st.metric(
        "BMI",
        f"{bmi:.2f}"
    )

with col2:
    st.metric(
        "BMI Category",
        category
    )


# ============================================================
# Healthy Weight Range
# ============================================================

st.subheader("Estimated Healthy Weight Range")

st.info(
    f"{min_normal_weight:.1f} kg – "
    f"{max_normal_weight:.1f} kg"
)


# ============================================================
# Recommended Weight Change
# ============================================================

st.subheader("Recommended Weight Change")

st.write(recommendation)


# ============================================================
# Advice
# ============================================================

st.subheader("Advice")

st.write(advice)


# ============================================================
# BMI Graph
# ============================================================

st.subheader("BMI Classification")

fig = create_bmi_graph(bmi)

st.pyplot(fig)

plt.close(fig)


# ============================================================
# Disclaimer
# ============================================================

st.caption(
    "Note: BMI is a screening measure and does not directly "
    "measure body fat or overall health. The recommended weight "
    "change shown here is a mathematical estimate based on BMI "
    "and should not be considered personalized medical advice."
)
