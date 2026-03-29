from core.database import engine, Base
from sqlalchemy import text

def reset_db_cascade():
    with engine.connect() as conn:
        print("Dropping all tables with CASCADE...")
        # Get all table names
        result = conn.execute(text("SELECT tablename FROM pg_tables WHERE schemaname = 'public'"))
        tables = [row[0] for row in result]
        
        for table in tables:
            print(f"Dropping {table}...")
            conn.execute(text(f"DROP TABLE IF EXISTS \"{table}\" CASCADE"))
        
        print("Dropping legacy types...")
        conn.execute(text("DROP TYPE IF EXISTS userrole CASCADE"))
        
        conn.commit()
    
    print("Recreating tables...")
    # Import all models to ensure they are registered with Base
    from models.user import User
    from models.test_category import TestCategory
    from models.survey_option import SurveyOption
    from models.question import Question
    from models.test_attempt import TestAttempt
    from models.question_result import QuestionResult
    from models.assessment_class_range import AssessmentClassRange
    
    Base.metadata.create_all(bind=engine)
    print("Database reset successful!")

if __name__ == "__main__":
    try:
        reset_db_cascade()
    except Exception as e:
        print(f"Error resetting database: {e}")
