// import_customers.js
const fs = require('fs');
const csv = require('csv-parser');
const { MongoClient } = require('mongodb');

const uri = 'mongodb://localhost:27017';
const dbName = 'customerdb';
const collectionName = 'customers';
const csvFilePath = '/docker-entrypoint-initdb.d/customers.csv';

(async () => {
  try {
    const client = new MongoClient(uri);
    await client.connect();
    const db = client.db(dbName);
    const collection = db.collection(collectionName);

    console.log('🚀 Importing customer data...');
    const customers = [];

    fs.createReadStream(csvFilePath)
      .pipe(csv())
      .on('data', (row) => {
        customers.push(row);
      })
      .on('end', async () => {
        await collection.insertMany(customers);
        console.log('✅ Customer data imported successfully');
        await client.close();
      });
  } catch (error) {
    console.error('❌ Error importing customer data:', error);
  }
})();
