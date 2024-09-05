export interface User{
    "id" : number,
    "username" : string,
    "first_name" : string,
    "last_name" : string,
    "email" : string,
    "token" : string
  }

export interface Team {
    "id" : number,
    "name" : string,
    "users" : number[],
    "created_at" : Date,
    "user" : number
  }

export interface Folder {
    "id" : number,
    "team" : Team,
    "parent_folder" : Folder,
    "owner" : User,
    "name" : string,
    "created_at" : Date,
    "updated_at" : Date
  }
  
  
export interface File_{
    file : File,
    folder : Folder,
    owner : User,
    name  : string,
    created_at : Date,
    updated_at : Date,
    file_extension : string
    id : number
  }

export interface Response{
    team : Team,
    folders : Folder[],
    files : File_[],
    folder_names_ids : string[][]
  }