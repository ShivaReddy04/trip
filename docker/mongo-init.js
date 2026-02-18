// MongoDB initialization script
// This runs when the container is first created

db = db.getSiblingDB('tripplanner');

// Create collections with validators
db.createCollection('users', {
  validator: {
    $jsonSchema: {
      bsonType: 'object',
      required: ['email', 'password', 'role', 'profile'],
      properties: {
        email: {
          bsonType: 'string',
          description: 'must be a string and is required'
        },
        password: {
          bsonType: 'string',
          description: 'must be a string and is required'
        },
        role: {
          enum: ['traveler', 'vendor', 'admin'],
          description: 'can only be one of the enum values'
        }
      }
    }
  }
});

db.createCollection('packages');
db.createCollection('bookings');
db.createCollection('reviews');
db.createCollection('ai_itineraries');

// Create indexes
db.users.createIndex({ email: 1 }, { unique: true });
db.users.createIndex({ role: 1 });
db.users.createIndex({ 'vendor.verified': 1 });

db.packages.createIndex({ slug: 1 }, { unique: true });
db.packages.createIndex({ vendorId: 1 });
db.packages.createIndex({ status: 1, category: 1 });
db.packages.createIndex({ status: 1, featured: 1 });
db.packages.createIndex({ tags: 1 });
db.packages.createIndex(
  { title: 'text', description: 'text', 'destinations.name': 'text' },
  { name: 'package_text_search' }
);

db.bookings.createIndex({ bookingId: 1 }, { unique: true });
db.bookings.createIndex({ userId: 1, status: 1 });
db.bookings.createIndex({ vendorId: 1, status: 1 });
db.bookings.createIndex({ packageId: 1 });

db.reviews.createIndex({ packageId: 1, status: 1 });
db.reviews.createIndex({ userId: 1 });

db.ai_itineraries.createIndex({ userId: 1, createdAt: -1 });

print('MongoDB initialization completed successfully!');
