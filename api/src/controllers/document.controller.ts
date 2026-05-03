import { Request, Response } from 'express'
import { PrismaClient } from '@prisma/client'
import fs from 'fs'

const prisma = new PrismaClient()

export async function createDocument(req: Request, res: Response) {
  const file = req.file

  if (!file) {
    res.status(400).json({ error: 'Nenhum arquivo enviado.' })
    return
  }

  const document = await prisma.document.create({
    data: {
      filename: file.originalname,
      filepath: file.path,
      totalChunks: 0,
    },
  })

  res.status(201).json(document)
}

export async function listDocuments(_req: Request, res: Response) {
  const documents = await prisma.document.findMany({
    orderBy: { createdAt: 'desc' },
  })

  res.json(documents)
}

export async function getDocument(req: Request, res: Response) {
  const { id } = req.params

  const document = await prisma.document.findUnique({ where: { id } })

  if (!document) {
    res.status(404).json({ error: 'Documento não encontrado.' })
    return
  }

  res.json(document)
}

export async function updateDocument(req: Request, res: Response) {
  const { id } = req.params
  const { totalChunks } = req.body

  const document = await prisma.document.findUnique({ where: { id } })

  if (!document) {
    res.status(404).json({ error: 'Documento não encontrado.' })
    return
  }

  const updated = await prisma.document.update({
    where: { id },
    data: { totalChunks },
  })

  res.json(updated)
}

export async function deleteDocument(req: Request, res: Response) {
  const { id } = req.params

  const document = await prisma.document.findUnique({ where: { id } })

  if (!document) {
    res.status(404).json({ error: 'Documento não encontrado.' })
    return
  }

  // Remove o arquivo do disco
  if (fs.existsSync(document.filepath)) {
    fs.unlinkSync(document.filepath)
  }

  // Cascata no banco remove conversas e chunks automaticamente
  await prisma.document.delete({ where: { id } })

  res.status(204).send()
}
