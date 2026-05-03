import { Request, Response } from 'express'
import { PrismaClient } from '@prisma/client'

const prisma = new PrismaClient()

export async function createConversation(req: Request, res: Response) {
  const { documentId, question, answer } = req.body

  if (!documentId || !question || !answer) {
    res.status(400).json({ error: 'documentId, question e answer são obrigatórios.' })
    return
  }

  const document = await prisma.document.findUnique({ where: { id: documentId } })

  if (!document) {
    res.status(404).json({ error: 'Documento não encontrado.' })
    return
  }

  const conversation = await prisma.conversation.create({
    data: { documentId, question, answer },
  })

  res.status(201).json(conversation)
}

export async function listConversations(req: Request, res: Response) {
  const { documentId } = req.query

  if (!documentId || typeof documentId !== 'string') {
    res.status(400).json({ error: 'Parâmetro documentId é obrigatório.' })
    return
  }

  const conversations = await prisma.conversation.findMany({
    where: { documentId },
    orderBy: { createdAt: 'asc' },
  })

  res.json(conversations)
}

export async function deleteConversation(req: Request, res: Response) {
  const { id } = req.params

  const conversation = await prisma.conversation.findUnique({ where: { id } })

  if (!conversation) {
    res.status(404).json({ error: 'Conversa não encontrada.' })
    return
  }

  await prisma.conversation.delete({ where: { id } })

  res.status(204).send()
}
