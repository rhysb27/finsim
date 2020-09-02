def generate_test_data():
    return { 
        'people': [
            {
                'name': 'Alice',
                'salary': {
                    'base_salary': '20000',
                    'pension': '4.0',
                    'payrise_rate': '5.0'
                },
                'expenses': {
                    'monthly': [
                        { 'name': 'Rent', 'cost': '400.00', 'inflation': False },
                    ]
                },
                'debts': [
                    {
                        'name': 'Credit Card',
                        'starting_balance': '2000.00',
                        'interest_rate': '0.00'
                    },
                    {
                        'name': 'Overdraft',
                        'starting_balance': '1500.00',
                        'interest_rate': '1.00'
                    }
                ],
                'savings': [
                    {
                        'name': 'Savings Acc.',
                        'interest_rate': '1.00',
                        'starting_balance': '0.00',
                        'type': 'traditional'
                    },
                    {
                        'name': 'Lifetime ISA',
                        'interest_rate': '1.05',
                        'starting_balance': '100.00',
                        'type': 'lisa'
                    }
                ]
            },
            {
                'name': 'Bob',
                'salary': {
                    'base_salary': '18000',
                    'pension': '0.0'
                },
                'expenses': {
                    'monthly': [
                        { 'name': 'Rent', 'cost': '400.00', 'inflation': False }
                    ]
                },
                'debts': [
                    {
                        'name': 'Overdraft',
                        'starting_balance': '1000.00',
                        'interest_rate': '0.00'
                    }
                ],
                'savings': [
                    {
                        'name': 'Lifetime ISA',
                        'starting_balance': '100.00',
                        'interest_rate': '1.05',
                        'type': 'lisa'
                    }
                ]
            }
        ],
        'group': {
            'expenses': {
                'monthly': [
                    { 'name': 'Groceries',      'cost': '500.00' },
                    { 'name': 'Car Insurance',  'cost': '100.00' }
                ],
                'annual': [
                    { 'name': 'Council Tax',     'cost': '1000.00' },
                    { 'name': 'Christmas Gifts', 'cost': '300.00', 'inflation': False }
                ]
            },
            'proportional_expenses': True
        }
    }
