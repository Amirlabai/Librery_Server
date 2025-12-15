import { HttpClient } from "@angular/common/http";
import { Injectable } from "@angular/core";
import { Observable } from "rxjs";
import { ApiConfigService } from "./api-config.service";



@Injectable({
  providedIn: 'root'
})
export class DashboardService {

    constructor(
      private http: HttpClient,
      private apiConfig: ApiConfigService
    ) {}
    
    private get baseUrl(): string {
      return this.apiConfig.getBackendUrl();
    }

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

    getPreviewUrl(item: any): string {
        if (item.is_folder || item.isFolder) {
            return ''; // Folders cannot be previewed
        } else {
            return `${this.baseUrl}/preview/${item.path}`;
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
    editFilePath(uploadId: number, newPath: string, oldPath:string): Observable<any> {

        return this.http.post(
            `${this.baseUrl}/admin/edit_upload_path/`,
            { upload_id: uploadId, new_path: newPath ,oldPath},
            { withCredentials: true }
        );
    }
    browse(path: string = ''): Observable<any> {
        const clean = path.replace(/^\/+|\/+$/g, '');
        const url = clean ? `${this.baseUrl}/browse/${clean}` : `${this.baseUrl}/browse`;
        return this.http.get(url, { withCredentials: true });
    }

    searchFiles(query: string,folderPath: string = ''): Observable<any> {
        return this.http.get(`${this.baseUrl}/search?q=${query}&folder_path=${folderPath}`, {
            withCredentials: true
        });
    }

    getUsefulLinks(): Observable<any> {
        return this.http.get(`${this.baseUrl}/useful_links`, {
            withCredentials: true
        });
    }
        

}