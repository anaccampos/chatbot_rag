/*
  Warnings:

  - You are about to drop the `document_chunks` table. If the table is not empty, all the data it contains will be lost.

*/
-- DropForeignKey
ALTER TABLE "document_chunks" DROP CONSTRAINT "document_chunks_document_id_fkey";

-- DropTable
DROP TABLE "document_chunks";
