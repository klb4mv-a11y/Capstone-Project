# Event Consumers - PostgreSQL Compatible
# In CQRS with PostgreSQL, events are primarily for logging and analytics

from events.event_bus import get_event_bus

# in-memory analytics storage (ephemeral session data)
_analytics_db = {
    'user_analytics': {},
    'system_stats': {
        'total_searches': 0,
        'total_users_created': 0,
        'total_favorites': 0
    }
}

def get_analytics_db():
    # get in-memory analytics database (for session analytics)
    return _analytics_db

def setup_event_consumers():
    """
    Setup event consumers for PostgreSQL-backed system.
    
    Note: With PostgreSQL, events are primarily used for:
    - Logging and audit trails
    - Analytics tracking
    - Triggering side effects
    """
    event_bus = get_event_bus()
    analytics_db = get_analytics_db()
    
    def on_user_created(event_data):
        user_id = event_data['data']['user_id']
        username = event_data['data']['username']
        
        # track analytics
        analytics_db['system_stats']['total_users_created'] += 1
        
        # log the event
        print(f"EVENT: User '{username}' created (ID: {user_id[:8]}...)")
    
    def on_user_profile_updated(event_data):
        user_id = event_data['data']['user_id']
        fields = event_data['data']['updated_fields']
        
        # log the event
        print(f"EVENT: User {user_id[:8]}... profile updated: {list(fields.keys())}")
    
    def on_ingredient_added(event_data):
        user_id = event_data['data']['user_id']
        ingredient_name = event_data['data']['ingredient_name']
        
        # log the event
        print(f"EVENT: Ingredient '{ingredient_name}' added to pantry")
    
    def on_ingredient_removed(event_data):
        user_id = event_data['data']['user_id']
        ingredient_id = event_data['data']['ingredient_id']
        
        # log the event
        print(f"EVENT: Ingredient removed from pantry")
    
    def on_recipe_favorited(event_data):
        user_id = event_data['data']['user_id']
        recipe_name = event_data['data']['recipe_name']
        
        # track analytics
        analytics_db['system_stats']['total_favorites'] += 1
        
        # log the event
        print(f"EVENT: Recipe '{recipe_name}' favorited")
    
    def on_recipe_unfavorited(event_data):
        user_id = event_data['data']['user_id']
        recipe_id = event_data['data']['recipe_id']
        
        # log the event
        print(f"EVENT: Recipe unfavorited")
    
    def on_recipe_search_performed(event_data):
        user_id = event_data['data']['user_id']
        ingredients = event_data['data']['ingredients']
        result_count = event_data['data']['result_count']
        
        # track analytics in memory
        if user_id not in analytics_db['user_analytics']:
            analytics_db['user_analytics'][user_id] = {
                'search_count': 0,
                'recent_searches': []
            }
        
        analytics_db['user_analytics'][user_id]['search_count'] += 1
        analytics_db['user_analytics'][user_id]['recent_searches'].append({
            'timestamp': event_data['timestamp'],
            'ingredients': ingredients,
            'result_count': result_count
        })
        
        # keep only last 10 searches
        if len(analytics_db['user_analytics'][user_id]['recent_searches']) > 10:
            analytics_db['user_analytics'][user_id]['recent_searches'].pop(0)
        
        # track system-wide analytics
        analytics_db['system_stats']['total_searches'] += 1
        
        # log the event
        print(f"📊 EVENT: Recipe search performed ({result_count} results)")
    
    def on_appliances_updated(event_data):
        user_id = event_data['data']['user_id']
        appliances = event_data['data']['appliances']
        
        # log the event
        print(f"📊 EVENT: User appliances updated ({len(appliances)} appliances)")
    
    # subscribe to all events
    event_bus.subscribe('USER_CREATED', on_user_created)
    event_bus.subscribe('USER_PROFILE_UPDATED', on_user_profile_updated)
    event_bus.subscribe('INGREDIENT_ADDED', on_ingredient_added)
    event_bus.subscribe('INGREDIENT_REMOVED', on_ingredient_removed)
    event_bus.subscribe('RECIPE_FAVORITED', on_recipe_favorited)
    event_bus.subscribe('RECIPE_UNFAVORITED', on_recipe_unfavorited)
    event_bus.subscribe('RECIPE_SEARCH_PERFORMED', on_recipe_search_performed)
    event_bus.subscribe('USER_APPLIANCES_UPDATED', on_appliances_updated)
    
    print(" Event Consumers Initialized (PostgreSQL Mode)")
    print("   - Events logged for audit trail")
    print("   - Analytics tracked in-memory")
    print("   - Data persisted in PostgreSQL")

def get_system_analytics():
    # get system-wide analytics
    return _analytics_db['system_stats']

def get_user_analytics(user_id: str):
    # get analytics for specific user
    return _analytics_db['user_analytics'].get(user_id, {
        'search_count': 0,
        'recent_searches': []
    })