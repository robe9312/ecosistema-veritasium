import { NextResponse } from 'next/server';
import Database from 'better-sqlite3';
import path from 'path';
import fs from 'fs';

export async function GET() {
  try {
    // Navigate up from dashboard/ to reach the root project
    const rootPath = path.join(process.cwd(), '../');
    const dbPath = path.join(rootPath, '.veritasium', 'state.db');
    
    if (!fs.existsSync(dbPath)) {
      // Mock data in case DB isn't initialized yet
      return NextResponse.json({ 
        trades: [],
        message: "No DB found yet" 
      });
    }

    const db = new Database(dbPath, { readonly: true });
    
    // Check if table exists
    const tableExists = db.prepare("SELECT name FROM sqlite_master WHERE type='table' AND name='trades'").get();
    if (!tableExists) {
      return NextResponse.json({ trades: [] });
    }

    const stmt = db.prepare('SELECT * FROM trades ORDER BY id ASC LIMIT 500');
    const trades = stmt.all();
    
    // Close DB
    db.close();
    
    return NextResponse.json({ trades });
  } catch (error: any) {
    return NextResponse.json({ error: error.message }, { status: 500 });
  }
}
