from openai import OpenAI
import pymysql
import json

api_key = "open AI API KEY"
client = OpenAI(api_key=api_key)

mysql_config = {
    'user': '',
    'password': '',
    'host': '',
    'database': '',
    'port': 3306,
    'charset': 'utf8mb4',
    'collation': 'utf8mb4_unicode_ci',
    'autocommit': True,
}

def generate_quiz_question():
    try:
        # OpenAI API 호출하여 퀴즈 질문 생성
        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": 'You are an economist. You have to create a quiz about the economy. Please provide the question and four choices in Korean, and specify the correct answer and reasoning. For example {"question": "What is inflation?","select": ["Inflation rise", "Decreased income", "There is no demand", "Production Forecast"],"Answer": "Inflation rise","Reason": "Inflation refers to a rise in prices, which occurs as a result of increasing prices in the economy as a whole."} Please write with this example. 다양한 경제에 대한 퀴즈를 만들어'},
            ]
        )
        
        # 생성된 퀴즈 질문 반환
        if completion.choices and len(completion.choices) > 0:
            message = completion.choices[0].message
            if message.content:
                return message.content
            else:
                print("응답에서 퀴즈 질문을 찾을 수 없습니다.")
                return None
        else:
            print("OpenAI API에서 유효한 응답을 받지 못했습니다.")
            print(f"API 응답: {completion}")
            return None
    
    except Exception as e:
        print(f"OpenAI API 호출 중 오류 발생: {e}")
        return None

def parse_quiz_question(content):
    try:
        if not content:
            print("퀴즈 질문이 유효하지 않습니다.")
            return None
        
        # JSON 문자열을 파싱
        question_data = json.loads(content)
        
        return question_data
    
    except json.JSONDecodeError as e:
        print(f"JSON 파싱 중 오류 발생: {e}")
        return None
    except Exception as e:
        print(f"퀴즈 질문 파싱 중 오류 발생: {e}")
        return None

def insert_into_mysql(parsed_question, mysql_config):
    try:
        conn = pymysql.connect(**mysql_config)
        cursor = conn.cursor()
        
        # 쿼리 작성 및 실행
        query = """
        INSERT INTO quiz
        (quiz, choice1, choice2, choice3, choice4, answer, reason) 
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        
        quiz = parsed_question.get('question')
        choices = parsed_question.get('select', [])
        answer = parsed_question.get('Answer')
        reason = parsed_question.get('Reason')
        
        while len(choices) < 4:
            choices.append('')
                
        cursor.execute(query, (quiz, choices[0], choices[1], choices[2], choices[3], answer, reason))
        
        conn.commit()
        print("데이터베이스에 질문이 성공적으로 추가되었습니다.")
        
    except pymysql.Error as err:
        print(f"MySQL 오류 발생: {err}")
        
    finally:
        if conn and conn.open:
            conn.close()
            print("MySQL 연결이 닫혔습니다.")

if __name__ == "__main__":
    try:
        repeat_count = int(input("퀴즈를 몇 번 생성하시겠습니까?: "))
        
        for _ in range(repeat_count):
            # 퀴즈 질문 생성 및 출력
            quiz_question = generate_quiz_question()
            if quiz_question:
                print("Generated Quiz Question:")
                print(quiz_question)
                
                # 퀴즈 질문 파싱
                parsed_question = parse_quiz_question(quiz_question)
                if parsed_question:
                    print("\nParsed Quiz Question:")
                    print(parsed_question)
                    
                    # MySQL에 퀴즈 질문 추가
                    insert_into_mysql(parsed_question, mysql_config)
                else:
                    print("퀴즈 질문 파싱 중 오류가 발생하여 MySQL에 추가하지 않습니다.")
            else:
                print("퀴즈 질문 생성 중 오류가 발생하여 MySQL에 추가하지 않습니다.")
    
    except ValueError:
        print("올바른 숫자를 입력해 주세요.")
    except KeyboardInterrupt:
        print("\n사용자에 의해 프로그램이 중단되었습니다.")
