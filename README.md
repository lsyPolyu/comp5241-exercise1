# NoteTaker - Personal Note Management Application

A modern, responsive web application for managing personal notes with a beautiful user interface and full CRUD functionality.

## 🌟 Features

- **Create Notes**: Add new notes with titles and rich content
- **Edit Notes**: Update existing notes with real-time editing
- **Delete Notes**: Remove notes you no longer need
- **Search Notes**: Find notes quickly by searching titles and content
- **Auto-save**: Notes are automatically saved as you type
- **Responsive Design**: Works perfectly on desktop and mobile devices
- **Modern UI**: Beautiful gradient design with smooth animations
- **Real-time Updates**: Instant feedback and updates
- **AI Translation**: Translate note content into a selected language and view the result separately

## 🛠 Technology Stack

### Frontend
- **HTML5**: Semantic markup structure
- **CSS3**: Modern styling with gradients, animations, and responsive design
- **JavaScript (ES6+)**: Interactive functionality and API communication

### Backend
- **Python Flask**: Web framework for API endpoints
- **SQLAlchemy**: ORM for database operations
- **Flask-CORS**: Cross-origin resource sharing support

### Database
- **SQLite**: Local development when `DATABASE_URL` is not set
- **PostgreSQL**: Used when `DATABASE_URL` is set, including on Vercel

## 📁 Project Structure

```
notetaking-app/
├── src/
│   ├── models/
│   │   ├── user.py          # User model (template)
│   │   └── note.py          # Note model with database schema
│   ├── routes/
│   │   ├── user.py          # User API routes (template)
│   │   ├── note.py          # Note API endpoints
│   │   └── translation.py   # DeepSeek translation endpoint
│   ├── database_config.py   # Database selection
│   └── main.py              # Flask application entry point
├── public/
│   ├── index.html           # Frontend application
│   └── favicon.ico          # Application icon
├── database/
│   └── app.db               # SQLite database file
├── venv/                    # Python virtual environment
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

## 🔧 Local Development Setup

### Prerequisites
- Python 3.11+
- pip (Python package manager)

### Installation Steps

1. **Clone or download the project**
   ```bash
   python -m venv venv
   ```

2. **Activate the virtual environment**
   ```bash
   source venv/bin/activate
   ```

   Remark: On Windows, use `venv\Scripts\activate`

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set translation configuration on the server (PowerShell example)**
   ```powershell
   $env:DEEPSEEK_API_KEY = Read-Host 'DeepSeek API Key'
   # Optional: $env:DEEPSEEK_MODEL = 'deepseek-flash'
   ```
   The default model is `deepseek-flash`; set `DEEPSEEK_MODEL` only to use another supported model.
   Set the key in the same terminal that starts Flask, then restart Flask if it is already running.
   `OPENAI_API_KEY` is not read by this translation endpoint.
   Keep the key out of source files and commits.

5. **Run the application**
   ```bash
   python src/main.py
   ```

6. **Access the application**
   - Open your browser and go to `http://localhost:5001`

## 📡 API Endpoints

### Notes API
- `GET /api/notes` - Get all notes
- `POST /api/notes` - Create a new note
- `GET /api/notes/<id>` - Get a specific note
- `PUT /api/notes/<id>` - Update a note
- `DELETE /api/notes/<id>` - Delete a note
- `GET /api/notes/search?q=<query>` - Search notes
- `POST /api/translate` - Translate text without changing or saving the note

Translation request: `{"text":"Hello","target_language":"fr"}`. The response is
`{"translation":"Bonjour"}`. Supported languages are `en`, `zh-CN`, `es`,
`fr`, `de`, `ja`, and `ko`. The endpoint requires `DEEPSEEK_API_KEY` in the server
environment and optionally reads `DEEPSEEK_MODEL`. The DeepSeek call uses Python's
standard library, so no additional package is needed. Run local API tests with
`python -m unittest discover -s tests -v`; a live provider test requires a real key.

### Request/Response Format
```json
{
  "id": 1,
  "title": "My Note Title",
  "content": "Note content here...",
  "created_at": "2025-09-03T11:26:38.123456",
  "updated_at": "2025-09-03T11:27:30.654321"
}
```

## 🎨 User Interface Features

### Sidebar
- **Search Box**: Real-time search through note titles and content
- **New Note Button**: Create new notes instantly
- **Notes List**: Scrollable list of all notes with previews
- **Note Previews**: Show title, content preview, and last modified date

### Editor Panel
- **Title Input**: Edit note titles
- **Content Textarea**: Rich text editing area
- **Translation**: Select a target language, translate the current content, and review the read-only result beside the original. Translation never saves or replaces the note.
- **Save Button**: Manual save option (auto-save also available)
- **Delete Button**: Remove notes with confirmation
- **Real-time Updates**: Changes reflected immediately

### Design Elements
- **Gradient Background**: Beautiful purple gradient backdrop
- **Glass Morphism**: Semi-transparent panels with backdrop blur
- **Smooth Animations**: Hover effects and transitions
- **Responsive Layout**: Adapts to different screen sizes
- **Modern Typography**: Clean, readable font stack

## 🔒 Database Schema

### Notes Table
```sql
CREATE TABLE note (
    id INTEGER PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    content TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

## 🚀 Deployment

### Vercel and Neon

Vercel uses the Flask `app` in `src/main.py`, selected explicitly by
`pyproject.toml`. `src/app.py` is an unrelated local test file and is excluded
from the deployment. Vercel serves `public/` directly; local Flask serves the
same files.

Create a Neon PostgreSQL database before deploying. In the Vercel project's
**Settings → Environment Variables**, configure:

- `DATABASE_URL` (required): the Neon PostgreSQL connection string, preferably
  the pooled connection string with SSL enabled.
- `DEEPSEEK_API_KEY` (required for translation): a DeepSeek API key.
- `DEEPSEEK_MODEL` (optional): defaults to `deepseek-flash`.
- `FLASK_SECRET_KEY` (optional for the current note features): needed if Flask
  sessions are added later.

Set variables for every Vercel environment you intend to use (Preview and/or
Production). `NOTETAKER_VERCEL=1` is supplied by `vercel.json` and makes the
app fail at startup if `DATABASE_URL` is missing; it never writes SQLite in a
Vercel function. The app creates its tables on startup. Do not put connection
strings or keys in source files, README, or Git. Local development without
`DATABASE_URL` continues to use `database/app.db`; this SQLite data is separate
from Neon and is not copied automatically.

Before deployment, run `python -m unittest discover -s tests -v`. After Neon is
created, verify the PostgreSQL connection and note create/read/update/delete
against that database, then check the Vercel Preview deployment before release.

## 🔧 Configuration

### Environment Variables
- `DATABASE_URL`: PostgreSQL when set; otherwise local SQLite
- `DEEPSEEK_API_KEY`: required for translation
- `DEEPSEEK_MODEL`: optional, defaults to `deepseek-flash`
- `FLASK_SECRET_KEY`: optional unless session features are used

### Database Configuration
- Local SQLite file: `database/app.db`
- Vercel database: PostgreSQL through `DATABASE_URL` (required)
- Automatic table creation on first run
- SQLAlchemy ORM for database operations

## 📱 Browser Compatibility

- Chrome/Chromium (recommended)
- Firefox
- Safari
- Edge
- Mobile browsers (iOS Safari, Chrome Mobile)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is open source and available under the MIT License.

## 🆘 Support

For issues or questions:
1. Check the browser console for error messages
2. Verify the Flask server is running
3. Ensure all dependencies are installed
4. Check network connectivity for the deployed version

## 🎯 Future Enhancements

Potential improvements for future versions:
- User authentication and multi-user support
- Note categories and tags
- Rich text formatting (bold, italic, lists)
- File attachments
- Export functionality (PDF, Markdown)
- Dark/light theme toggle
- Offline support with service workers
- Note sharing capabilities

---

**Built with ❤️ using Flask, SQLite, and modern web technologies**

