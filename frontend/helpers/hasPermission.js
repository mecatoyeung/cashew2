import CryptoJS from 'crypto-js'

export default function hasPermission(checkingPermission) {
  let allPermissions = JSON.parse(
    CryptoJS.AES.decrypt(
      localStorage.getItem('permissions'),
      'sonikgloballimited'
    ).toString(CryptoJS.enc.Utf8)
  )
  return allPermissions.includes(checkingPermission)
}
