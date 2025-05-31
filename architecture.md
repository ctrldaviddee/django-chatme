+-------------------+       +-------------------+       +-------------------+
| auth_user | | Room | | Message |
+-------------------+       +-------------------+       +-------------------+
| id (PK) |<----- | id (PK) |<----- | id (PK) |
| username | | name | | room_id (FK) ---->| Room
| email | | slug (Unique) | | sender_id (FK) -->| auth_user
|... | | is_private | | content |
+-------------------+ | created_at | | timestamp |
          ^ | created_by_id (FK)| | message_type |
| +-------------------+ | is_read |
| | reply_to_id (FK) |
| | forwarded_from_id |
| +-------------------+
+-------------------+                                             ^
| Profile | |
+-------------------+ |
| id (PK) | +-------------------+
| user_id (FK) ---->| auth_user | MediaAttachment |
| profile_picture | +-------------------+
| bio | | id (PK) |
| status_message | | message_id (FK) -->| Message
+-------------------+ | file |
| file_type |
| file_size |
| thumbnail |
| uploaded_at |
                                                        +-------------------+

+-------------------+
| RoomMembership | (Optional intermediary table for ManyToMany)
+-------------------+
| id (PK) |
| user_id (FK) ---->| auth_user
| room_id (FK) ---->| Room
| joined_at |
| role |
+-------------------+