// MongoDB initialization script for DXP Component Generator
// This script runs when the MongoDB container starts for the first time

// Switch to the application database
db = db.getSiblingDB('aem_component_generator');

// Create a user for the application
db.createUser({
  user: 'dxp_user',
  pwd: 'dxp_password',
  roles: [
    {
      role: 'readWrite',
      db: 'aem_component_generator'
    }
  ]
});

// Create initial collections with indexes
db.createCollection('chat_sessions');
db.createCollection('chat_messages');
db.createCollection('generated_components');

// Create indexes for better performance
db.chat_sessions.createIndex({ "session_id": 1 }, { unique: true });
db.chat_sessions.createIndex({ "user_id": 1 });
db.chat_sessions.createIndex({ "created_at": 1 });
db.chat_sessions.createIndex({ "is_active": 1 });

db.chat_messages.createIndex({ "session_id": 1 });
db.chat_messages.createIndex({ "created_at": 1 });
db.chat_messages.createIndex({ "sender": 1 });

db.generated_components.createIndex({ "session_id": 1 });
db.generated_components.createIndex({ "component_name": 1 });
db.generated_components.createIndex({ "created_at": 1 });

print('MongoDB initialization completed for DXP Component Generator');
