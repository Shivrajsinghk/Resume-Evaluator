import os, json, time
from dotenv import load_dotenv
from pydantic import BaseModel
from groq import Groq
from pypdf import PdfReader
from docx import Document
from pathlib import Path

load_dotenv()

api = os.getenv('GROQ_API_KEY')
if not api:
    raise ValueError("API Key not found!!!")

model = 'openai/gpt-oss-20b'
client = Groq(api_key=api)

job_description = f'''
    RIVR, an Amazon company, is building Physical AI by deploying autonomous robots for real-world doorstep delivery. Operating daily in diverse urban environments, RIVR's robots continuously learn from and navigate the millions of scenarios encountered during deliveries. By owning the full stack from software to hardware, RIVR is purpose-built for safety, reliability, and the customer from day one.
    As our next Senior Backend Engineer you will focus on the design, development, and operation of the server-side systems that power our robotics delivery platform. This role involves building robust, scalable microservices and integrations crucial for fleet operations, process integrations, and data processing in a cloud-native environment. You will play a key part in translating complex business requirements into reliable and efficient backend solutions.
    Key job responsibilities
    Design and implement backend services for integrating RIVR's platform with our customers’ systems, to provide delightful delivery experiences.
    Develop and enhance the backend infrastructure for our robot operations platform.
    Develop backend components to aggregate Key Performance Indicators (KPIs), providing insights into platform performance and business value.
    Contribute to the overall architecture, reliability, and scalability of our backend systems within a containerized microservices context.
    Collaborate closely with frontend, robotics, and infrastructure engineers to deliver end-to-end features
    Basic Qualifications
    - 5 years of professional experience designing, building, deploying, and operating backend systems in a Service-Oriented Architecture (SOA) context.
    - Strong experience with Typescript, Java, C++ and/or Python
    - Different interaction patterns (e.g. RPC, publish/subscribe, event-driven).
    - At least two database technologies
    - Demonstrable experience in at least one of the following areas:
    - Integrating with complex third-party APIs and building reliable, distributed workflows (e.g., using task queues, state machines).
    - Building event-driven applications and/or scalable data processing pipelines (e.g., using Kafka, message queues, serverless functions).
    - Willingness to participate in on-call rotations
    Preferred Qualifications
    - Familiarity configuring and operating CI/CD pipelines.
    - Background in robotics, IoT, fleet management, or real-time data streaming systems.
    - Strong familiarity with observability such as OTLP, Grafana, prometheus, etc preferably in the context of devices with intermittent connectivity
    Amazon is an equal opportunities employer. We believe passionately that employing a diverse workforce is central to our success. We make recruiting decisions based on your experience and skills. We value your passion to discover, invent, simplify and build. Protecting your privacy and the security of your data is a longstanding top priority for Amazon. Please consult our Privacy Notice (https://www.amazon.jobs/en/privacy_page) to know more about how we collect, use and transfer the personal data of our candidates.
    Our inclusive culture empowers Amazonians to deliver the best results for our customers. If you have a disability and need a workplace accommodation or adjustment during the application and hiring process, including support for the interview or onboarding process, please visit https://amazon.jobs/content/en/how-we-hire/accommodations for more information. If the country/region you’re applying in isn’t listed, please contact your Recruiting Partner.
    '''

def parse_job_description(job_description):
    class JobDescription(BaseModel):
        role: str
        required_skills: list[str]
        preferred_skills: list[str]
        minimum_experience: float | None
        education_requirements: list[str]

    job_desciption_schema = JobDescription.model_json_schema()
    
    system_prompt = f"""
    You are an expert HR assistant.
    Your job is to analyze job descriptions and extract
    structured information from them.
    Return ONLY valid JSON matching this schema:
    {job_desciption_schema}
    IMPORTANT:
    Do NOT return the schema itself.
    Do NOT return fields like "properties", "title" or "type".
    Fill the schema with actual information extracted from the job description.
    If minimum experience is not mentioned, return null.
    If information for a list is missing, return an empty list.
    Do not invent information.
    """

    user_prompt = f"""
    Analyze the following job description:
    {job_description}
    """

    system_message = {
        'role': 'system',
        'content': system_prompt
    }
    user_message = {
        'role': 'user',
        'content': user_prompt
    }
    response_format = {
        'type': 'json_object'
    }

    messages = [system_message, user_message]

    response = client.chat.completions.create(
        model=model,
        messages=messages,
        response_format=response_format
    )

    ans = response.choices[0].message.content
    raw_json = json.loads(ans)
    job = JobDescription(**raw_json)

    return job

def parse_resume(resume_text):
    class Experience(BaseModel):
        company: str | None = None
        role: str | None = None
        duration: str | None = None
        description: str | None = None
        skills_used: list[str] = []

    class Resume(BaseModel):
        name: str | None = None 
        age: int | None = None
        email: str | None = None
        total_experience_years: float | None = None
        skills: list[str] = []
        experience: list[Experience] = []
        education: list[str] = []
        projects: list[str] = []
        certifications: list[str] = []

    resume_schema = Resume.model_json_schema()

    system_prompt = f"""
    You are an expert resume parser.
    Extract information from the resume based on its meaning,
    not only based on exact section headings.
    Different resumes may use different headings.
    For example:
    - Experience
    - Professional Experience
    - Work History
    - Employment
    - Internships
    These may all contain relevant experience.
    Skills may also appear in the skills section, work experience,
    internships or projects.
    Return ONLY valid JSON matching this schema:
    {resume_schema}
    Important rules:
    1. Do not invent information.
    2. If a value is not available, return null.
    3. If a list has no information, return an empty list.
    4. Include internships inside experiences.
    5. Extract skills mentioned across the entire resume.
    """

    user_prompt = f"""
    Parse the following resume:
    {resume_text}
    """

    system_message = {
        'role': 'system',
        'content': system_prompt
    }
    user_message = {
        'role': 'user',
        'content': user_prompt
    }
    response_format = {
        'type': 'json_object'
    }

    messages = [system_message, user_message]

    response = client.chat.completions.create(
        model=model,
        messages=messages,
        response_format=response_format
    )

    ans = response.choices[0].message.content
    raw_json = json.loads(ans)
    resume = Resume(**raw_json)

    return resume

def final_scoring(job, resume):
    class MatchResults(BaseModel):
        score: int
        details: dict

    match_results_schema = MatchResults.model_json_schema()
    
    prompt = f"""
    You are an HR recruiter.
    Compare the candidate's resume with the job description.
    JOB DESCRIPTION:
    {job.model_dump_json(indent=2)}
    CANDIDATE RESUME:
    {resume.model_dump_json(indent=2)}
    Return JSON matching this schema:
    {match_results_schema}
    Give me:
    1. Candidate name
    2. Matching skills
    3. Missing important skills
    4. Whether experience requirement is met
    5. Overall match percentage from 0 to 100
    6. A short final verdict
    Keep the response concise and easy to read
    """

    message = {
        'role': 'user',
        'content': prompt
    }
    response_format = {
        'type': 'json_object'
    }

    messages = [message]

    response = client.chat.completions.create(
        model=model,
        messages=messages,
        response_format=response_format
    )

    ans = response.choices[0].message.content
    raw_json = json.loads(ans)
    results = MatchResults(**raw_json)

    return results

def read_pdf(file_path):
    reader = PdfReader(file_path)
    text = ""
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"
    return text

def read_docx(file_path):
    document = Document(file_path)
    text = ""
    for paragraph in document.paragraphs:
        para_text = paragraph.text
        if para_text.strip():
            text += para_text + "\n"
    for table in document.tables:
        for row in table.rows:
            for cell in row.cells:
                cell_text = cell.text
                if cell_text.strip():
                    text += cell_text + "\n"
    return text

def read_resume(file_path):
    if file_path.suffix.lower() == '.pdf':
        return read_pdf(file_path)
    elif file_path.suffix.lower() == '.docx':
        return read_docx(file_path)
    else:
        return None

resumes_folder_path = Path('resumes')

# Scores will be a list of dictionaries
scores = []

# iterdir is used to iterate over files and folder inside a directory
for file_path in resumes_folder_path.iterdir():
    if file_path.suffix.lower() not in ('.pdf', '.docx'):
        continue    
    print("\nProcessing the resume of", file_path.stem, '...')
    
    resume_text = read_resume(file_path)
    parsed_resume = parse_resume(resume_text)

    time.sleep(5)

    # Job and resume are the pydantic objects
    job = parse_job_description(job_description)
    final_score = final_scoring(job, parsed_resume)
    # This final_score is a pydantic object which has score and details

    time.sleep(5)

    scores.append(final_score.model_dump()) 
    # This step converts a pydantic object into a python dictionary

scores.sort(key=lambda candidate: candidate['score'], reverse=True)

for score in scores:
    print(score, '\n')
    