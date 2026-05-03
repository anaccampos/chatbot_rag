import { Router } from 'express'
import {
  createConversation,
  listConversations,
  deleteConversation,
} from '../controllers/conversation.controller'

const router = Router()

router.post('/', createConversation)
router.get('/', listConversations)
router.delete('/:id', deleteConversation)

export default router
