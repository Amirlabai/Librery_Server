# API Endpoint Naming Analysis

## Current Issues vs REST Best Practices

### ❌ Issues Found

#### 1. **Inconsistent Naming Convention**
- **Mixed kebab-case and snake_case:**
  - ✅ kebab-case: `/forgot-password`, `/reset-password`, `/refresh-session`
  - ❌ snake_case: `/create_folder`, `/my_uploads`
  - **Recommendation:** Use **kebab-case** consistently (industry standard for URLs)

#### 2. **Verbs in URLs (Not RESTful)**
- ❌ `/browse` - Should be `/files` or `/directories`
- ❌ `/create_folder` - Should be `POST /folders`
- ❌ `/delete/<path>` - Should be `DELETE /files/<path>`
- ❌ `/search` - Should be `GET /files?q=...` (query parameter)
- ❌ `/suggest` - Should be `POST /suggestions`
- ❌ `/approve`, `/deny`, `/toggle-role`, `/toggle-status` - Actions should be part of resource

#### 3. **Improper HTTP Method Usage**
- ❌ `POST /delete/<path>` - Should be `DELETE /files/<path>`
- ❌ `POST /create_folder` - Should be `POST /folders`

#### 4. **Inconsistent Resource Naming**
- ❌ `/my_uploads` vs `/admin/uploads` - Should be `/uploads` with query params or `/users/me/uploads`
- ❌ `/browse` - Not a resource name, should be `/files` or `/directories`

#### 5. **Action-Based Endpoints (Not RESTful)**
- ❌ `/admin/approve/<email>` - Should be `PUT /admin/users/<email>` with status in body
- ❌ `/admin/toggle-role/<email>` - Should be `PATCH /admin/users/<email>/role`
- ❌ `/admin/move_upload/<filename>` - Should be `PUT /admin/uploads/<id>/status`

---

## ✅ Recommended RESTful API Structure

### Authentication
```
POST   /auth/login              ✅ (or /auth/sessions)
POST   /auth/register           ✅ (or /auth/users)
POST   /auth/logout             ✅ (or DELETE /auth/sessions)
POST   /auth/password/forgot    ✅
POST   /auth/password/reset     ✅
GET    /auth/session/refresh    ✅ (or GET /auth/me)
```

### File Management
```
GET    /files                   ✅ Browse root (was /browse)
GET    /files/<path>            ✅ Browse directory (was /browse/<path>)
GET    /files/<path>/download   ✅ Download file (was /download/file/<path>)
GET    /files/<path>/download?format=zip  ✅ Download folder (was /download/folder/<path>)
GET    /files/<path>/preview    ✅ Preview file (was /preview/<path>)
GET    /files?q=<query>         ✅ Search files (was /search)
POST   /folders                 ✅ Create folder (was /create_folder)
DELETE /files/<path>            ✅ Delete file (was POST /delete/<path>)
```

### Uploads
```
POST   /uploads                 ✅ Upload file(s) (was /upload)
GET    /uploads                 ✅ Get user's uploads (was /my_uploads)
GET    /uploads?status=pending  ✅ Get pending uploads (was /admin/uploads)
PUT    /uploads/<id>/approve    ✅ Approve upload (was /admin/move_upload)
DELETE /uploads/<id>            ✅ Decline upload (was /admin/decline_upload)
PATCH  /uploads/<id>/path       ✅ Edit upload path (was /admin/edit_upload_path)
```

### Admin
```
GET    /admin/metrics           ✅ System metrics
GET    /admin/metrics/logs/<type>/download  ✅ Download logs (was /admin/metrics/download/<log_type>)
GET    /admin/users             ✅ List users
GET    /admin/users?status=pending  ✅ Pending users (was /admin/pending)
GET    /admin/users?status=denied  ✅ Denied users (was /admin/denied)
PUT    /admin/users/<email>/status  ✅ Approve/deny (was /admin/approve, /admin/deny)
PATCH  /admin/users/<email>/role   ✅ Toggle role (was /admin/toggle-role)
PATCH  /admin/users/<email>/status ✅ Toggle status (was /admin/toggle-status)
POST   /admin/users/<email>/re-pend ✅ Re-pend (was /admin/re-pend)
POST   /admin/sessions/heartbeat ✅ Heartbeat (was /admin/heartbeat)
```

### Suggestions
```
POST   /suggestions             ✅ Submit suggestion (was /suggest)
GET    /suggestions             ✅ Get suggestions (if needed)
```

---

## Industry Standards Reference

### REST API Naming Conventions:
1. **Use nouns, not verbs** - Resources are things, not actions
2. **Use plural nouns** - Collections should be plural (`/users`, `/files`)
3. **Use kebab-case** - URLs should use lowercase with hyphens
4. **Use HTTP methods properly:**
   - GET - Read/Retrieve
   - POST - Create
   - PUT - Full update
   - PATCH - Partial update
   - DELETE - Delete
5. **Use query parameters** - For filtering, searching, pagination
6. **Use hierarchical structure** - `/resource/<id>/sub-resource`

### Examples from Major APIs:
- **GitHub API:** `/repos/{owner}/{repo}/issues`
- **Stripe API:** `/customers/{id}`, `/charges/{id}/refund`
- **Twitter API:** `/tweets/{id}`, `/users/{id}/tweets`
- **Google Cloud API:** `/projects/{project}/datasets/{dataset}`

---

## Priority Recommendations

### High Priority (Breaking Changes)
1. ✅ Standardize to **kebab-case** throughout
2. ✅ Change `/browse` to `/files`
3. ✅ Change `POST /delete` to `DELETE /files/<path>`
4. ✅ Change `/create_folder` to `POST /folders`

### Medium Priority (Improvements)
1. ✅ Change `/search` to `/files?q=...`
2. ✅ Change `/my_uploads` to `/uploads` or `/users/me/uploads`
3. ✅ Change `/suggest` to `POST /suggestions`

### Low Priority (Nice to Have)
1. ✅ Refactor admin action endpoints to use PATCH/PUT
2. ✅ Use query parameters for filtering (`?status=pending`)

---

## Migration Strategy

If you want to maintain backward compatibility:
1. Keep old endpoints but mark as deprecated
2. Add new RESTful endpoints
3. Update frontend gradually
4. Remove old endpoints in next major version

Example:
```python
# Old (deprecated)
@files_bp.route("/browse", methods=["GET"])
def browse_old():
    return redirect("/files", code=301)

# New (RESTful)
@files_bp.route("/files", methods=["GET"])
def browse_new():
    # ... implementation
```

