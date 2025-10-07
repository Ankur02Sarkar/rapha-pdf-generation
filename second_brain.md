# Second Brain: RaphaCure PDF Generation API

## 🛠️ Stack
- **Language:** Python
- **Framework:** FastAPI
- **PDF Generation:** WeasyPrint
- **Template Engine:** Jinja2
- **Validation:** Pydantic v2
- **Package Manager:** uv

## 🎯 Current Focus
- ✅ **COMPLETED:** Successfully transformed the API into a PDF generation service with prescription and invoice endpoints.
- ✅ **COMPLETED:** AWS Lambda deployment configuration with Mangum adapter and containerized deployment.

## 🗺️ API Endpoint Map
- `GET /health` - Public (Application health check)
- `POST /api/v1/pdf/prescription` - Public (Generate prescription PDF)
- `POST /api/v1/pdf/invoice` - Public (Generate invoice PDF)
- `GET /api/v1/pdf/health` - Public (PDF service health check)
- `GET /api/v1/pdf/templates/info` - Public (Template information)

## 🚀 AWS Lambda Deployment
- **Lambda Function:** `rapha-pdf-generation-lambda`
- **Runtime:** Python 3.10 (Container)
- **Handler:** `main.handler` (Mangum adapter)
- **Memory:** 512MB (configurable)
- **Timeout:** 30 seconds (configurable)
- **Architecture:** x86_64

## 📝 To-Do List (Next Actions)
- ✅ All initial development tasks completed successfully
- ✅ AWS Lambda deployment scripts and configuration completed
- [ ] **DEPLOYMENT:** Execute `./deploy.sh` to deploy to AWS Lambda
- [ ] **TESTING:** Run `python test_lambda_deployment.py` to validate deployment
- [ ] **API Gateway:** Deploy CloudFormation template for API Gateway integration
- [ ] **Future Enhancement:** Add more PDF templates (e.g., medical reports, receipts)
- [ ] **Future Enhancement:** Implement PDF template customization options
- [ ] **Future Enhancement:** Add PDF watermarking capabilities
- [ ] **Future Enhancement:** Implement batch PDF generation

## 🐞 Known Issues / Refactors
- ✅ **RESOLVED:** WeasyPrint system dependencies installed (pango, gdk-pixbuf, libffi)
- ✅ **RESOLVED:** Pydantic v2 compatibility issues fixed (regex → pattern)
- [ ] **Future:** Consider adding PDF caching for frequently generated documents
- [ ] **Future:** Add comprehensive error logging and monitoring

## 🏛️ Architectural Decisions
- **API Versioning:** All endpoints use `/api/v1` prefix for future compatibility
- **PDF Response Format:** Base64-encoded PDF data suitable for frontend consumption
- **Template Architecture:** HTML templates with embedded CSS for maintainability
- **Validation Strategy:** Comprehensive Pydantic schemas with detailed field validation
- **Service Layer:** Clean separation between API endpoints and PDF generation logic
- **Error Handling:** Standardized error responses with detailed error messages

## 🧪 Testing Status
- ✅ **PDF Service Health:** Operational with WeasyPrint v66.0 and Jinja2 v3.1.6
- ✅ **Prescription PDF:** Successfully generates 15KB+ PDFs with valid PDF headers
- ✅ **Invoice PDF:** Successfully generates 17KB+ PDFs with proper formatting
- ✅ **Base64 Encoding:** Verified compatibility with frontend PDF consumption

## 📊 Performance Metrics
- **Prescription PDF Generation:** ~15KB average file size
- **Invoice PDF Generation:** ~17KB average file size
- **Response Format:** Base64-encoded strings (20K+ characters)
- **Template Rendering:** Jinja2 with embedded CSS for optimal performance