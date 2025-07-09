from backend.jd_analyzer import analyze_job_description

sample_jd = """
We are seeking a Clinical Data Analyst with expertise in SQL, Python, and Tableau. 
Responsibilities include managing healthcare datasets, generating dashboards, and ensuring HIPAA compliance.
Preferred: knowledge of EDC systems, SAS, and experience in oncology trials.
Education: Master's in Health Informatics or related field.
"""

result = analyze_job_description(sample_jd)
print(result)
