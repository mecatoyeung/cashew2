import { useState, useEffect, useRef, useMemo, useCallback } from 'react'
import { useRouter } from 'next/router'
import Image from 'next/image'

import { produce } from 'immer'

import { Form } from 'react-bootstrap'
import { Modal } from 'react-bootstrap'
import { Button } from 'react-bootstrap'
import { Dropdown } from 'react-bootstrap'
import { Row, Col } from 'react-bootstrap'

import Select from 'react-select'

import Loader from '../../../../assets/icons/loader.svg'

import SettingsLayout from '../../../../layouts/settings'

import service from '../../../../service'

import accountStyles from '../../../../styles/Account.module.css'

import _UserForm from '../_form'

export default function Users() {
  return <_UserForm type="edit" />
}
