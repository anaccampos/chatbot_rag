import { Router } from 'express'
import { upload } from '../middlewares/upload.middleware'
import {
  createDocument,
  listDocuments,
  getDocument,
  updateDocument,
  deleteDocument,
} from '../controllers/document.controller'

const router = Router()

router.post('/', upload.single('file'), createDocument)
router.get('/', listDocuments)
router.get('/:id', getDocument)
router.patch('/:id', updateDocument)
router.delete('/:id', deleteDocument)

export default router
