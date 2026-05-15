import axios from 'axios'

export const api = axios.create({
    baseURL: '',
    timeout: 30000,
})

export function downloadJson(filename, data) {
    const content = JSON.stringify(data, null, 2)
    const blob = new Blob([content], { type: 'application/json;charset=utf-8' })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = filename
    document.body.appendChild(link)
    link.click()
    link.remove()
    URL.revokeObjectURL(url)
}
