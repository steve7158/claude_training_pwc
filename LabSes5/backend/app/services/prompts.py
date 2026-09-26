from app.models.schemas import Patient


def _format_patient_context(patient: Patient) -> str:
    visits = "\n".join(f"- {v.date}: {v.note}" for v in patient.visit_history)
    return (
        f"Patient: {patient.name}, {patient.age} y/o {patient.sex}\n"
        f"Problem list: {', '.join(patient.problem_list)}\n"
        f"Medications: {', '.join(patient.medications)}\n"
        f"Allergies: {', '.join(patient.allergies)}\n"
        f"Vitals/labs: {', '.join(f'{k}={v}' for k, v in patient.vitals.items())}\n"
        f"Visit history (most recent first):\n{visits}"
    )


def build_summarize_prompt(patient: Patient) -> str:
    context = _format_patient_context(patient)
    return (
        "You are a clinical documentation assistant helping a physician quickly review a "
        "patient's chart before an appointment. Summarize the following chart in a concise "
        "clinical brief (under 150 words): active problems, current medications, any notable "
        "trends across visits (e.g. improving/worsening labs), and anything that may need "
        "follow-up. Use plain clinical language, no filler.\n\n"
        f"{context}\n\n"
        "Summary:"
    )


def build_draft_note_prompt(patient: Patient, raw_text: str) -> str:
    context = _format_patient_context(patient)
    return (
        "You are a clinical documentation assistant. Draft a structured SOAP note (Subjective, "
        "Objective, Assessment, Plan) from the physician's raw encounter notes below, using the "
        "patient's chart for background context. Only include objective findings, medications, "
        "and history explicitly present in the chart or raw notes below — do not invent findings, "
        "labs, or history not provided. Use clear clinical language and standard SOAP headings.\n\n"
        f"Patient chart context:\n{context}\n\n"
        f"Physician's raw encounter notes for today's visit:\n{raw_text}\n\n"
        "SOAP Note:"
    )
