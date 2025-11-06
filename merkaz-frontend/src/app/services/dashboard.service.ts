import { HttpClient } from "@angular/common/http";
import { Injectable } from "@angular/core";
import { Observable } from "rxjs";



@Injectable({
  providedIn: 'root'
})
export class DashboardService {

    private baseUrl = 'http://localhost:8000';

    constructor(private http: HttpClient) {}

    loadFiles(path: string = ''): Observable<any> {

        const url = path
            ? `${this.baseUrl}/browse/${path}`
            : `${this.baseUrl}/browse`;
            return this.http.get(url, { withCredentials: true });
    }

    getDownloadUrl(item: any): string {

        if (item.is_folder || item.isFolder) {
            return `${this.baseUrl}/download/folder/${item.path}`;
        } else {
            return `${this.baseUrl}/download/file/${item.path}`;
        }
    }

    deleteItem(path: string): Observable<any> {

        const url = `${this.baseUrl}/delete/${path}`;
        return this.http.post(url, {}, { withCredentials: true });
    }

    logout(): Observable<any> {

        return this.http.post(`${this.baseUrl}/logout`, {}, { withCredentials: true });
    }

    submitSuggestion(suggestion: string): Observable<any> {
        return this.http.post(
                `${this.baseUrl}/suggest`,
                { suggestion },
                { withCredentials: true }
        );
    }

    createFolder(parentPath: string, folderName: string): Observable<any> {

        return this.http.post(
                `${this.baseUrl}/create_folder`,
                {
                parent_path: parentPath,
                folder_name: folderName
                },
                { withCredentials: true }
        );
    }

    editFilePath(uploadId: number, newPath: string): Observable<any> {
        return this.http.post(
            `${this.baseUrl}/edit_upload_path`,
            { upload_id: uploadId, new_path: newPath },
            { withCredentials: true }
        );
    }

    browse(path: string = ''): Observable<any> {
        const clean = path.replace(/^\/+|\/+$/g, '');
        const url = clean ? `${this.baseUrl}/browse/${clean}` : `${this.baseUrl}/browse`;
        return this.http.get(url, { withCredentials: true });
    }
}