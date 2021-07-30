import pandas as pd

class TransformApps15():
    def __init__(self):
        pass

    def fit(self, X:pd.DataFrame, Y:pd.DataFrame or pd.Series):
        return self
        
    def transform(self, X:pd.DataFrame, y = None) -> pd.DataFrame:
        leave_columns = ['loan_amount', 'loan_days', 'gender_id', 'marital_status_id', 'children_count_id', 'education_id', 'addr_region_id', 'addr_owner_type_id', 
                 'fact_addr_same', 'fact_addr_region_id', 'fact_addr_owner_type_id', 'has_immovables', 'has_movables', 'employment_type_id', 'position_id',
                 'organization_type_id', 'organization_branch_id', 'empoyees_count_id', 'seniority_years', 'has_prior_employment', 'monthly_income',
                 'income_frequency_id', 'income_source_id', 'monthly_expenses', 'other_loans_about_current', 'other_loans_about_monthly',
                 'product_dpr', 'product_amount_from', 'product_amount_to', 'product_overdue_dpr', 'product_interest_min', 'applied_at', 'purpose_other',
                 'birth_date', 'passport_date', 'email', 'position_other', 'organization_type_other']
        X = X[leave_columns]

        X = X.replace('[]', '', regex=False)
        X['email'] = X['email'].str.split('@', expand=True)[1]

        X['passport_year'] = pd.to_datetime(X['passport_date'], format='%Y-%m-%d', errors='coerce').dt.year
        del X['passport_date']

        X['birth_year'] = pd.to_datetime(X['birth_date'], format='%Y-%m-%d', errors='coerce').dt.year
        del X['birth_date']

        X['applied_at'] = pd.to_datetime(X['applied_at'], format='%Y-%m-%d %H', errors='coerce')
        X['applied_day'] = X['applied_at'].dt.day
        X['applied_weekday'] = X['applied_at'].dt.weekday
        X['applied_hour'] = X['applied_at'].dt.hour
        del X['applied_at']

        return X

    def target_transform(self, Y:pd.DataFrame) -> pd.DataFrame:
        Y['target'] = Y['status_id']
        Y['target'].loc[Y['status_id'] == 1] = 0
        Y['target'].loc[Y['status_id'] == 5] = 1
        return Y['target']