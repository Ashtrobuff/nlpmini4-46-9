import streamlit as st
import re
from PyPDF2 import PdfReader
import docx
import matplotlib.pyplot as plt

# Read resume text from PDF file
def read_pdf(file):
    pdf_reader = PdfReader(file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text

# Read resume text from DOC/DOCX file
def read_docx(file):
    doc = docx.Document(file)
    full_text = []
    for para in doc.paragraphs:
        full_text.append(para.text)
    return "\n".join(full_text)

# Read resume text from file based on type
def read_resume(file, file_type):
    if file_type == "pdf":
        return read_pdf(file)
    elif file_type == "docx" or file_type == "doc":
        return read_docx(file)
    else:
        return file.read().decode('utf-8')  # For txt files

# Extract contact info (email, phone) using regex
def extract_contact_info(text):
    email = re.findall(r"[a-zA-Z0-9+_.-]+@[a-zA-Z0-9.-]+", text)
    phone = re.findall(r"\(?\+?\d{1,3}?\)?-?\s?\d{1,4}-?\s?\d{1,4}-?\s?\d{4}", text)
    return {
        "Email": email[0] if email else None,
        "Phone": phone[0] if phone else None
    }

# Extract name (assume name is the first capitalized word in the resume)
def extract_name(text):
    name_match = re.match(r"^[A-Z][a-z]+\s[A-Z][a-z]+", text)  # Assumes name is at the top of the resume
    return name_match.group() if name_match else "Not found"

# Extract organizations (companies/universities) using regex patterns
def extract_organizations(text):
    org_pattern = r"\b(?:Inc|Corporation|Corp|Ltd|LLC|University|College|Institute)\b"
    orgs = re.findall(fr"[A-Z][a-zA-Z\s]*(?:{org_pattern})", text)
    return orgs if orgs else ["Not found"]

# Extract dates (experience or education periods)
def extract_dates(text):
    date_pattern = r"\b(?:\d{2}/\d{4}|\d{4})\b"
    dates = re.findall(date_pattern, text)
    return dates if dates else ["Not found"]

# Extract job titles by looking for common job title words
def extract_job_titles(text):
    job_titles = ['Engineer', 'Manager', 'Developer', 'Consultant', 'Analyst', 'Designer', 'Architect', 'Technician']
    titles_found = []
    for title in job_titles:
        if title.lower() in text.lower():
            titles_found.append(title)
    return titles_found if titles_found else ["Not found"]

# Extract skills using a predefined list
def extract_skills(text):
    skills_list = ['Python', 'Java', 'C++', 'JavaScript', 'SQL', 'HTML', 'CSS', 'Machine Learning', 
                   'Data Analysis', 'React', 'Django', 'Flask', 'TensorFlow', 'Keras', 'AWS', 
                   'Docker', 'Kubernetes', 'Leadership', 'Communication', 'Problem-solving']

    skills_found = [skill for skill in skills_list if skill.lower() in text.lower()]
    return skills_found if skills_found else ["No skills found"]

# Give a resume score based on presence of key elements
def calculate_resume_score(name, contact_info, organizations, dates, job_titles, skills):
    score = 0
    if name != "Not found": score += 10
    if contact_info['Email']: score += 10
    if contact_info['Phone']: score += 10
    if organizations != ["Not found"]: score += 20
    if dates != ["Not found"]: score += 20
    if job_titles != ["Not found"]: score += 20
    if skills != ["No skills found"]: score += 10
    return score

# Visualization for the resume score using a pie chart
def plot_resume_score(score):
    labels = 'Scored', 'Remaining'
    sizes = [score, 100 - score]
    colors = ['#00C851', '#ff4444']
    explode = (0.1, 0)  # explode the scored slice

    fig, ax = plt.subplots()
    ax.pie(sizes, explode=explode, labels=labels, colors=colors, autopct='%1.1f%%',
           shadow=True, startangle=90)
    ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
    return fig

# Streamlit app
def main():
    st.title("Multi Resume Parser and Ranking")

    uploaded_files = st.file_uploader("Upload multiple resumes (.pdf, .doc, .docx, .txt)", type=["pdf", "doc", "docx", "txt"], accept_multiple_files=True)

    if uploaded_files:
        resume_data = []
        for uploaded_file in uploaded_files:
            file_type = uploaded_file.name.split('.')[-1].lower()

            # Read the resume
            resume_text = read_resume(uploaded_file, file_type)
            st.subheader(f"Resume: {uploaded_file.name}")

            # Extract sections and entities
            contact_info = extract_contact_info(resume_text)
            name = extract_name(resume_text)
            organizations = extract_organizations(resume_text)
            dates = extract_dates(resume_text)
            job_titles = extract_job_titles(resume_text)
            skills = extract_skills(resume_text)

            # Calculate resume score
            resume_score = calculate_resume_score(name, contact_info, organizations, dates, job_titles, skills)
            
            # Store resume info and score for ranking
            resume_data.append((name, resume_score, uploaded_file.name, contact_info, organizations, dates, job_titles, skills))

        # Rank resumes based on score
        resume_data.sort(key=lambda x: x[1], reverse=True)

        st.subheader("Resume Ranking")
        for idx, (name, score, filename, _, _, _, _, _) in enumerate(resume_data):
            st.write(f"{idx + 1}. {filename} - Score: {score}/100")

        # Select a resume for detailed analysis
        selected_resume = st.selectbox("Select a resume for detailed analysis", [r[2] for r in resume_data])

        if selected_resume:
            for resume in resume_data:
                if resume[2] == selected_resume:
                    name, score, _, contact_info, organizations, dates, job_titles, skills = resume

                    st.subheader(f"Detailed Analysis for {selected_resume}")
                    st.write(f"**Name**: {name}")
                    st.write(f"**Email**: {contact_info['Email']}")
                    st.write(f"**Phone**: {contact_info['Phone']}")
                    st.write(f"**Organizations**: {', '.join(organizations)}")
                    st.write(f"**Dates**: {', '.join(dates)}")
                    st.write(f"**Job Titles**: {', '.join(job_titles)}")
                    st.write(f"**Skills**: {', '.join(skills)}")

                    # Show score pie chart
                    score_chart = plot_resume_score(score)
                    st.pyplot(score_chart)

if __name__ == '__main__':
    main()
