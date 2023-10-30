import { useState, useEffect, useRef, useMemo, useCallback } from 'react'
import { useRouter } from 'next/router'
import Image from 'next/image'

import { produce } from 'immer'

import { Form } from 'react-bootstrap'
import { Modal } from 'react-bootstrap'
import { Button } from 'react-bootstrap'
import { Dropdown } from 'react-bootstrap'
import { Accordion } from 'react-bootstrap';

import Select from 'react-select'

import WorkspaceLayout from '../../../../../../layouts/workspace'

import service from '../../../../../../service'

import PreProcessingForm from './_orientationDetectionForm'

export default function PreProcessing() {

  const router = useRouter()

  const { parserId, preprocessingId } = router.query

  const [preProcessing, setPreProcessing] = useState(null)

  const getPreProcessing = () => {
    if (!preprocessingId) return
    service.get("/preprocessings/" + preprocessingId + "/", (response) => {
      setPreProcessing(response.data)
    })
  }

  useEffect(() => {
    getPreProcessing()
  }, [parserId, preprocessingId])

  return (
    <>
      {preProcessing && preProcessing.preProcessingType == "ORIENTATION_DETECTION" && (
        <PreProcessingForm type="edit" />
      )}
    </>
  )
}
