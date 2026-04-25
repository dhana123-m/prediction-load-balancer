def balance_system(prediction):

    if prediction == "High":
        return "Server B Activated"

    elif prediction == "Medium":
        return "Balanced Between A & B"

    else:
        return "Primary Server A Running"